import bs4
import requests
from bs4 import BeautifulSoup

import pandas as pd
import time

import argparse
import os

def scrape_indeed(jobTitle, Location=None, salary=None, output=None, *args, **kwargs):

    jobTitle = jobTitle.replace(" ","+")
    salary = salary.replace("$","").replace(",","")
    Location = Location.replace(" ","+")
    # scrape the website and acquire top 100 resulting data points

    results = {
        'jobTitle':[],
        'company':[],
        'location':[],
        'relativeLocation':[],
        'jobSummary':[]
    }
    ## Iterating through the top 100 jobs. 
    for pageNumber in range(1, 100, 10):

        ## Generate a URL String with search criteria
        URL = "https://www.indeed.com/jobs?q={}+${}&l={}&start={}".format(jobTitle, salary, Location, pageNumber)

        ## populating a BS html object for the given URL
        page = requests.get(URL)
        soup = BeautifulSoup(page.text, 'html.parser')

        ## Iterating through each of the fields on the page
        for div in soup.find_all(name='div', attrs={'class':'row','data-tn-component':'organicJob'}):
            ### Getting job title information
            for a in div.find_all(name='a', attrs={'data-tn-element':'jobTitle'}):
                results['jobTitle'].append(a['title'])
            
            ### Getting Company information
            company = div.find_all(name='span', attrs={'class':'company'})
            if len(company)>0:
                name = company[0]
                results['company'].append(name.text.strip())
            else:
                results['company'].append("No Company Listed")
            
            ### Getting location information
            location = div.find_all(name='span', attrs={'class':'location'})
            if len(location)>0:    
                name = location[0]
                results['location'].append(name.text.strip())
            else:
                results['location'].append('No Location Listed')
            
            results['relativeLocation'].append(Location.replace('+'," "))
            ### Getting job summary information
            summary = div.find_all(name='span', attrs={'class':'summary'})
            if len(summary)>0:
                name = summary[0]
                results['jobSummary'].append(name.text.strip())
            else:
                results['jobSummary'].append('No Job Summary Provided')
    
    ## Store the data in a data frame object 
    results = pd.DataFrame(results)

    ## Saves output (optional) and returns data frame
    if output is not None:
        results.to_csv(output,sep='|',index=False)
    else:
        results.to_csv('{}_{}.csv'.format(Location.replace(',',""),jobTitle))
    
    return results

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-j','--jobTitle',help="Job Title to search for.", required=True)
    parser.add_argument('-l','--location',help='Location to search for the specified job.', required=False)
    parser.add_argument('-s','--salary',help='Salary to search.',required=False)
    parser.add_argument('-o','--output',help="Output file name.", required=False)

    args = parser.parse_args()
    
    out = pd.DataFrame()
    for Location in ['Chicago, IL', 'New York, NY', 'Orlando, FL', 'Seatle, WA', 'San Francisco, CA', 'Atlanta, GA', 'Las Vegas, NV', 'Lincoln, NE', 'Miami, FL', 'Tampa, FL']:
        temp = scrape_indeed(args.jobTitle, Location = Location, salary = args.salary)
        out = pd.concat([out,temp])
    
    print(out.relativeLocation.value_counts())
    out.to_csv('AllCities.csv',sep="|",index=False)