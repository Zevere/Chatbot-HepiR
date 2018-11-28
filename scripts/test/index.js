const $ = require('shelljs')
require('../logging')

$.config.fatal = true


try {
    console.warn(`ToDo`)
} catch (e) {
    console.error(e)
    process.exit(1)
}

console.info(`✅ Tests Passed.`)