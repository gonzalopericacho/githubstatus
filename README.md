Github Status
=========

Parallelized script that calls the Github API for retrieving the status of an organization's repositories.

## Usage

What you only need to do is create an environment variable called GITHUB_TOKEN, setting it with a Github token, and run the script. For creating a Github token you should access to settings -> Personal Access Tokens -> Generate new token, and generate it with default configuration. To create an environment variable run this command in the CLI:

        export GITHUB_TOKEN=<my-token>

replacing `<mytoken>` with your Github token.


## Docker usage

    docker run -e GITHUB_TOKEN=*my-token* -t gonzalopericacho/github_status

replacing `*my-token*` with your Github token.


## Dependencies

* Python
* gevent library
* tabulate library
* requests library

## Notes

* The script is meant to retrieve the status of an organization's repositories. If you want to retrieve user repositores you should delete the line with the `no user repos` comment.
* The output shows two tables: 
    * The first table: used for major repositories which have at least an staging branch (default branch) and a master branch. The table shows:
        *  The name of the repos
        *  Its last release
        *  number of commits staying is behind and ahead master.
        *  number of issues
        *  number of pull requests
        *  The staus of the tests on master and staging: `x`denotes that at least one test fail, `*` denotes that no test failed but at least one is pending, &#10003; denotes that all test finished successfully.
        *  Additional notes: when the last release does not point to the last commit of master branch it will be printed `release missing`; when the master has commits ahead of staging it will be printed `staging needs rebasing`.
    *  The Second table: used for minor repositories. The table shows:
        *  The name of the repos
        *  number of issues
        *  number of pull requests
        *  number of stars
        *  number of forks
*  **All** requests to the Github API are done in parallel using gevent. The script should take less than 10 seconds to gather all the data. 