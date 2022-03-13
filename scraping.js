// to perform get requests
import axios from 'axios'
// to parse dom
import cheerio from 'cheerio'
// to manipulate files
import fs from 'fs'

// async func since we are calling a distant server
// it will create an array of objects with year and idArticles as keys, and the corresponding
// year and array of ids for this year
export const getLegifranceData = async () => {
  // will try to do that, if errors arise will go to catch block
  try {
    // each book is scraped one by hand and you have to change it manually
    /**   CGI: 'https://www.legifrance.gouv.fr/codes/texte_lc/LEGITEXT000006069577/',
          CGI1: 'https://www.legifrance.gouv.fr/codes/texte_lc/LEGITEXT000006069568/',
          CGI2: 'https://www.legifrance.gouv.fr/codes/texte_lc/LEGITEXT000006069569/',
          CGI3: 'https://www.legifrance.gouv.fr/codes/texte_lc/LEGITEXT000006069574/',
          CGI4: 'https://www.legifrance.gouv.fr/codes/texte_lc/LEGITEXT000006069576/',
          LPF: 'https://www.legifrance.gouv.fr/codes/texte_lc/LEGITEXT000006069583/',
    */
    // THE FILE NAME MUST BE CHANGED AT THE END ALSO !!

    // url of the book
    const url =
      'https://www.legifrance.gouv.fr/codes/texte_lc/LEGITEXT000006069576/'
    // empty array that will contain our data
    const jsonAllYears = []
    // we iterate over the years
    for (let year = 1980; year < 2023; year++) {
      // we get our data from the server, we go to the summary of the book and
      // search for all ids of articles
      const { data } = await axios({
        method: 'GET',
        // I used the 2nd of January not to be bothered by changing articles on the 1st
        url: url + `${year}-01-02/`,
      })

      // we load data into cheerio
      const $ = cheerio.load(data)

      // we search for selector
      const selector = '.articleLink'
      // links is going to be a cheerio object
      const links = $(selector)

      // this array will contain all ids for the year we are in in the for-loop
      const idArticlesArray = []
      // we extract the id in the url and put in in our array for the year we are in
      links.each((i, el) => {
        idArticlesArray.push($(el).attr('href').split('#')[1])
      })
      // once we have all ids we append them to our main array with keys year and idArticles
      jsonAllYears.push({
        year: year,
        idArticles: idArticlesArray,
      })
    }
    // fs.writeFileSync('CGI4_1980_2022id.json', JSON.stringify(jsonAllYears))
    // we return the array
    return jsonAllYears
    //if an error happens we log it in the console
  } catch (err) {
    console.log(err)
  }
}

// we use this list to convert our months to english to use javascript methods after
const frToEn = {
  janvier: 'january',
  février: 'february',
  mars: 'march',
  avril: 'april',
  mai: 'may',
  juin: 'june',
  juillet: 'july',
  août: 'august',
  septembre: 'september',
  octobre: 'october',
  novembre: 'november',
  décembre: 'december',
}

// this function is going to take care of dates to convert them to timestamps
const getDate = input => {
  const date = input.split(' ')
  const day = date[0]
  const month = frToEn[date[1].toLowerCase()]
  const year = date[2]
  return new Date(`${year}, ${month}, ${day}`)
}

// this asynchronous function is going to be performed for each article
// it will take the whole array of objects composed of a year key and an idArticles key with the whole array of each articles' id for this year
const getEachArticle = async obj => {
  try {
    // the root of the url for articles
    const url = `https://www.legifrance.gouv.fr/codes/article_lc/`

    // i is only used to print in console our progress in our scraping
    let i = 0
    // we create an empty array to host our data
    const articles = []
    // this for of loop will loop through the array
    for (const item of obj) {
      // for each object representing each year it will log the year
      console.log(item.year)
      // iterate over each id articles
      for (const id of item.idArticles) {
        // fire fetchData function to get the article
        const article = await fetchData(id, item, url)
        i++
        // we check if our function fetchData does send something back not to pollute our array in case of.
        if (article != undefined) {
          // we print our progress in console and we add our created article to the articles array
          console.log(i, article.name)
          articles.push(article)
        }
      }
    }
    // we create a file with our created articles once we are done
    fs.writeFileSync('CGI4_1980_2022.json', JSON.stringify(articles))
    return articles
  } catch (err) {
    // if there is an issue we log it to the console
    console.log(err)
  }
}

// this async function is going to scrape the content of the webpage of the article
// it will organize the relevant data in an object called article in which we have
// year, name, enacting date, rescinding date, url, path, depth, content

// the function takes 3 parameters, the id of the article, the item we are in in our given array
// corresponding to a batch of ids with a given year, and the root url
const fetchData = async (id, item, url) => {
  try {
    // we perform a get request to the retrieve the data, I used the 2nd of february not to be
    // bothered by articles enacted the 1st of January
    const { data } = await axios({
      method: 'GET',
      url: url + `${id}/${item.year}-01-02/`,
    })
    // we create our date
    const date = new Date(item.year, 2, 1).getTime()
    // we load the html into cheerio
    const $ = cheerio.load(data)

    // this is going to check if the page sends an Erreur (happened only once)
    // we do not return anything
    const error1 = $('.main-header-title').text().includes('Erreur')
    if (error1) {
      console.log('broken')
      return
    }

    // we get the name of the article
    const name = $('.name-article').text()
    const version_vigueur = $('.version-article').text()
    // it can happen that an article is in the code but not enacted and we don't want future articles
    if (version_vigueur.includes('A venir')) {
      console.log('A venir')
      return
    }
    // we format our dates
    if (version_vigueur.includes('au')) {
      var from = getDate(
        version_vigueur.split(' du ')[1].split(' au ')[0]
      ).getTime()
      var to = getDate(
        version_vigueur.split(' du ')[1].split(' au ')[1]
      ).getTime()
    } else {
      var from = getDate(version_vigueur.split(' le ')[1]).getTime()
      var to = new Date(2022, 1, 20).getTime()
    }
    // we get the text of the article
    const content = $('.list-article-consommation .content').text()
    const paths = $('a.title-link')
    const path = []
    // we put the path in our array path
    paths.each((i, el) => {
      if ($(el).text() != '') {
        path.push($(el).text())
      }
    })
    // we check if the article has not been rescinded because there are still such articles
    if (name.includes('abrogé') && date > to) {
      console.log('Abrogé')
      return
    } else {
      // we create our article object with useful information
      const article = {
        year: item.year,
        name: name.split('(abrogé)')[0].trim(), //.split('Article ')[1]
        from: from,
        to: to,
        // id: id,
        url: url + `${id}/${item.year}-01-02/`,
        depth: path.length,
        // CGI : Code Général des Impôts
        // CGI1 : Code Général des Impôts Annexe 1
        // CGI2 : Code Général des Impôts Annexe 2
        // CGI3 : Code Général des Impôts Annexe 3
        // CGI4 : Code Général des Impôts Annexe 4
        // LPF: Livre des Procédures Fiscales
        path: ['Code Général des Impôts Annexe 4', ...path],
        content: content.trim(),
      }
      // we return the article
      return article
    }
  } catch (err) {
    console.log('error detected, waiting 3s')
    // if we are blocked by Legifrance because it's using some tools to prevent DDOS attacks, we wait 3s and retry
    await waitFor(3000)
    return await fetchData(id, item, url)
  }
}

// this function is used to wait for 3s if an error arises
const waitFor = x => new Promise(resolve => setTimeout(resolve, x))

// this is going to monitor the whole process, first we get articles' id then we
// get each article from these ids
const scrapingProcess = async () => {
  const legifranceData = await getLegifranceData()
  console.log('All articles IDs added to json archive')
  // we take our array of objects containing year and idArticles as a parameter
  const eachArticle = await getEachArticle(legifranceData)
  console.log('All articles added to json archive')
}

// we execute the main function
scrapingProcess()
