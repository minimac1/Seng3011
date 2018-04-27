
# Team Turtle's API Testing Script


## Usage

  To start the tests run 'runTests.py'. You will then be prompted what APIs you would like to test, the APIs are described below

  ### Command Line Output
     When running the testing script you will first be asked what APIs you want to test.
     After the script will then run out tests against each API, it will tell you how close it is to finishing each API's testing.
     At the end it will tell you how many tests were passed, failed, and skipped.

  ### List of Testable APIs
   * Turtle Online: The current version of our API run on our AWS server. Does not skip any tests.
   * Turtle Local:  The current version of our API run locally on your own computer. To correctly run this test you must make sure our API is running locally on the same device.
   * Penguin:       The current version of team Penguin's API. Does not skip any tests.
   * Rooster Hawk:  The current version of team Rooster Hawk's API. Skips any tests checking if incorrect company names are rejected, since Rooster does not reject invalid company names.
   * Lion:          The current version of team Lion's API. Skips any tests checking if incorrect company names are rejected, since Lion does not reject invalid company names.

## Output

  Once each APIs tests are done they will then output a file called `*API Name* Out.txt`.
   * At the start of the file are how many tests passed, failed, skipped, and the time/duration of all the tests.
   * After there is a line for each test describing whether the tests was passed, failed, or skipped.
   * Each line also includes the expected output and the received output, aswell as the URL used to query the API
