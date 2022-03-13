import fs from 'fs'

var data1 = JSON.parse(fs.readFileSync('CGI_1980_2022_r.json'))
var data2 = JSON.parse(fs.readFileSync('CGI1_1980_2022_r.json'))
var data3 = JSON.parse(fs.readFileSync('CGI2_1980_2022_r.json'))
var data4 = JSON.parse(fs.readFileSync('CGI3_1980_2022_r.json'))
var data5 = JSON.parse(fs.readFileSync('CGI4_1980_2022_r.json'))
var data6 = JSON.parse(fs.readFileSync('LPF_1980_2022_r.json'))

const merged = [...data1, ...data2, ...data3, ...data4, ...data5, ...data6]

fs.writeFileSync('CGI_r.json', JSON.stringify(merged))
