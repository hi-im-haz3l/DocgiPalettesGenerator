import fs from 'fs'
import fetch from "node-fetch"
import dotenv from "dotenv"

dotenv.config()

const rawData = fs.readFileSync('manifest.json')
const jsonData = JSON.parse(rawData)

var errors = []

function sleep(ms) {
    return new Promise((resolve) => {
      setTimeout(resolve, ms);
    });
  }

for (let i = 0; i < jsonData.length; i++) {
    var currentBook = jsonData[i]
    
    var cover_image = fs.readFileSync(currentBook.image_paths[0])
    cover_image = new Buffer(cover_image).toString('base64')

    const payloads = {
        method: 'POST',
        headers: {'x-api-key': process.env.API_SECRET},
        body: JSON.stringify({
            "title": currentBook.title,
            "author": currentBook.author,
            "publisher": currentBook.publisher,
            "color_palette": currentBook.color_palette,
            "cover_image": `data:image/webp;base64,${cover_image}`
        })
    };

    await fetch(process.env.API_ENDPOINT, payloads)
    .then(async response => {
        const { message: message, err: err } = await response.json()
        if (response.status === 200) {
            console.log(message)
        }
        else if ([401,409,403,410].includes(response.status)) {
            console.log(`${response.status} - ${message}`)
            process.exit()
        }
        else {
            const error = `${response.status} - ${response.statusText} | ${err} | ${currentBook.title}`
            console.log(error)
            errors.push(error)
        }
        console.log(`Progress: ${i+1}/${jsonData.length}`)
        await sleep(100)
    })
    .catch(err => errors.push(err))
}

console.log(`Stats: ${jsonData.length - errors.length} completed, ${errors.length} errors`)
console.log(errors)
