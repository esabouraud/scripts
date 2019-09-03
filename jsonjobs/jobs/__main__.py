"""Get jobs offer from json stream"""

import re
import argparse
import json
import urllib3

urllib3.disable_warnings()


def get_jobs_json(url):
    """Get jobs json payload"""

    http = urllib3.PoolManager()
    req = http.request("GET", url)
    return req.data


def display_jobs(jobs_json, joburl_prefix, filter_rx):
    """Filter and display job offers"""

    jobs = json.loads(jobs_json)
    for job in jobs["items"]:
        match = filter_rx.search(json.dumps(job))
        if not match:
            print("%s - %s => %s%s" % (job["title"], job["fulllocation"], joburl_prefix, job["id"]))


def main():
    """Run script"""

    parser = argparse.ArgumentParser(
        prog="jobs", description="jobs filter")
    parser.add_argument(
        "-f", "--filter", dest="filter", default=None, help="Exclude jobs that match this regexp")
    parser.add_argument(
        dest="url", default=None, help="URL for jobs json stream")
    parser.add_argument(
        dest="joburl_prefix", default=None, help="URL prefix for outgoing link")
    options = parser.parse_args()

    print("Fetching jobs from: %s" % options.url)
    jobs_json = get_jobs_json(options.url)
    if options.filter:
        filter_rx = re.compile(options.filter)
    else:
        filter_rx = None
    display_jobs(jobs_json, options.joburl_prefix, filter_rx)


if __name__ == "__main__":
    main()
