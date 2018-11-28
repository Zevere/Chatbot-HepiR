const $ = require('shelljs')
const path = require('path')
require('../logging')

$.config.fatal = true
const root = path.join(__dirname, '..', '..')

try {
    const image_name = 'chatbot-hepir:latest'
    console.info(`building Docker Image "${image_name}"`)
    $.cd(root)
    $.exec(`docker build --no-cache --tag ${image_name} .`)
} catch (e) {
    console.error(e)
    process.exit(1)
}

console.info(`✅ Build succeeded`)