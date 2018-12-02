const $ = require('shelljs')
const path = require('path')
require('../logging')

$.config.verbose = true
const root = path.join(__dirname, '..', '..')


try {
    const image_name = 'chatbot-hepir-tests:latest'
    console.info(`building Docker Image "${image_name}"`)
    $.cd(`${root}`)
    $.exec(`docker build --tag ${image_name} -f ${root}/Dockerfile.tests .`)
    let pytest_result = $.exec(`docker run --rm ${image_name} pytest`).code
    /**
        * From pytest documentation:
        * https://docs.pytest.org/en/latest/usage.html#possible-exit-codes
        */
    switch (pytest_result) {
        case 0:
            console.info('Pytest => All tests were collected and passed successfully')
            break;
        case 1:
            console.error('Pytest => Tests were collected and run but some of the tests failed')
            process.exit(1)
            break;
        case 2:
            console.error('Pytest => Test execution was interrupted by the user')
            process.exit(2)
            break;
        case 3:
            console.error('Pytest => Internal error happened while executing tests')
            process.exit(3)
            break;
        case 4:
            console.error('Pytest => pytest command line usage error')
            process.exit(4)
            break;
        case 5:
            console.error('Pytest => No tests were collected')
            process.exit(5)
            break;
    }
} catch (e) {
    console.error(e)
    process.exit(1)
}

console.info(`✅ Tests Passed.`)