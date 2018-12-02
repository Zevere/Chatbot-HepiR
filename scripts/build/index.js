const $ = require('shelljs')
const path = require('path')
require('../logging')

$.config.fatal = true
const root = path.resolve(`${__dirname}/../..`)

try {
    console.info(`building Docker images`)

    $.cd(root)

    console.debug('building the final image with the "chatbot-hepir:latest" tag')
    $.exec(`docker build --tag chatbot-hepir --no-cache --target final .`)

    console.debug('building the tests image with the "chatbot-hepir:test" tag')
    $.exec(`docker build --tag chatbot-hepir:test --no-cache --target test .`)
} catch (e) {
    console.error(e)
    process.exit(1)
}

console.info(`✅ Build succeeded`)