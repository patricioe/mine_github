__author__ = 'patricioe'

#!/usr/bin/env python

from github3 import login
from optparse import OptionParser
from getpass import getuser, getpass
import readline
from fullcontact import FullContact


# http://github3py.readthedocs.org/en/latest/repos.html
# https://github.com/sigmavirus24/github3.py

def fetchFullContact(fc, email):
    fc_profile = fc.get(email=email)

    # gender, country, linkedin, current_job, title
    res = ["","","","",""]

    if fc_profile is None:
        return res

    if 'demographics' in fc_profile:
        if 'gender' in fc_profile['demographics']:
            res[0] = fc_profile['demographics']['gender'].encode('ascii','ignore')
        if 'locationGeneral' in fc_profile['demographics']:
            res[1] = fc_profile['demographics']['locationGeneral'].encode('ascii','ignore')

    if 'socialProfiles' in fc_profile:
        for li in fc_profile['socialProfiles']:
            if li['typeId'].encode('ascii','ignore') == 'linkedin':
                res[2] = li['url'].encode('ascii','ignore')
                break

    if 'organizations' in fc_profile:
        res[3] = fc_profile['organizations'][0]['name'].encode('ascii','ignore')
        res[4] = fc_profile['organizations'][0]['title'].encode('ascii','ignore')

    return res


def printRepoResults(repo, committers, score, fc):
    for key, val in committers:
        keyToUse = key.split(",")
        name = keyToUse[0].encode('ascii','ignore')
        email = keyToUse[1].encode('ascii','ignore')
        fullcontact_list = fetchFullContact(fc, email)
        list_of_fields = [name, email, val, repo.html_url, score] + fullcontact_list
        print '"'+'","'.join(unicode(x) for x in list_of_fields)+'"'


def trackCommiter(commit, committers):
    key = "%s,%s" % (commit.author['name'], commit.author['email'])
    committers[key] = committers.get(key, 0) + 1


def processCommits(gh, repo, score, fc):
    committers = {}
    repoToUse = gh.repository(repo.owner.login, repo.name)
    for c in repoToUse.iter_commits(number=1000):
        trackCommiter(c.commit, committers)
    printRepoResults(repo, sorted(committers.items()), score, fc)


def searchGH(gh, options, fc):
    query = '%s+language:%s' % (options.query, options.lang)
    res = gh.search_repositories(query, sort='stars', order='desc', per_page=None, text_match=False, number=-1,
                                 etag=None)

    for r in res:
        #print ("Url: %s - Score: %s " % (r.repository.html_url, r.score))
        processCommits(gh, r.repository, r.score, fc)


def main():
    '''
    main(): Expect a query to search for and a language.
    '''
    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option("-o", "--output_file", dest="output_file",
                      help="file to write output to. If file exists already, it will be overwritten.")
    parser.add_option("-q", "--query", dest="query", help="the query string for example: angularjs")
    parser.add_option("-l", "--language", dest="lang", help="the language of the repo")

    (options, args) = parser.parse_args()

    user = raw_input('Prompt (enter github username): ')

    #while not password:
    password = getpass('Password for {0}: '.format(user))

    gh = login(user, password)

    fc = FullContact('<YOUR_FC_API>')

    searchGH(gh, options, fc)


if __name__ == '__main__':
    main()
