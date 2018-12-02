const $ = require('shelljs')
require('../logging')

$.config.fatal = true

try {
    console.info(`Running HepiR unit tests`)

    const exec_result = $.exec(
        `docker run --rm --tty ` +
        `--env "TOKEN=FOO" ` +
        `chatbot-hepir:test`
    )

    /**
     * From pytest documentation:
     * https://docs.pytest.org/en/latest/usage.html#possible-exit-codes
     */
    switch (exec_result.code) {
        case 0:
            console.debug('Pytest => All tests were collected and passed successfully')
            break;
        case 1:
            throw 'Pytest => Tests were collected and run but some of the tests failed'
        case 2:
            throw 'Pytest => Test execution was interrupted by the user'
        case 3:
            throw 'Pytest => Internal error happened while executing tests'
        case 4:
            throw 'Pytest => pytest command line usage error'
        case 5:
            throw 'Pytest => No tests were collected'
    }
} catch (e) {
    console.error(e)
    process.exit(1)
}

console.info(`✅ Tests Passed.`)