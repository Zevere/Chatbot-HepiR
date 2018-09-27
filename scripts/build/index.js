const $ = require('shelljs')
const path = require('path')
require('../logging')

$.config.fatal = true
const root = path.join(__dirname, '..', '..')
const dist_dir = path.join(root, 'dist')

const docker_script = require('./build_docker_image')

function clear() {
    console.info('Clearing dist directory')

    $.rm('-rf', `${root}/dist`)
    $.mkdir('-p', `${root}/dist/app/`)
}

try {
    clear()
    docker_script.build_image()
} catch (e) {
    console.error(e)
    process.exit(1)
}

console.info(`Build succeeded: "${path.join(dist_dir, 'app')}"`)