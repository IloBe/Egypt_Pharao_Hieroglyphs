#!/usr/bin/env -S python3 -i

"""
Web application about egypt pharaoh names and their dynasties. Main entry point.

The egypt_pharaohs_dynasties.csv dataset includes needed information about
names, transliterations and images
(https://github.com/IloBe/Egypt-Pharaoh-Hieroglyphs/blob/main/Egypt_Pharaoh_Hieroglyphs/data/egypt_pharaohs_dynasties.csv).
This csv file is stored in the general projects data directory.
On the landing page, some background information about the pharaoh names is given.
Then with the callback’s Input, Output arguments we display another page when a dynasty or period is selected. 

Note:
All relevant Python libraries are stored in the virtual environment which is activated to run this code.
Regarding Cross-Site Request Forgery (CSRF) protection, which is an attack that uses the
victim’s credentials to perform undesired actions on behalf of the victim, by default this protection is
automatically applied to all forms in a Dash app. The CSRF token is included in the form submission and
validated on the server side to prevent cross-site request forgery attacks.
Furthermore, this main.py file is modified, so, SSL handling can be activated if cert files are available.

Author: Ilona Brinkmeier
Date: Nov. 2023
"""

##########################
# imports
##########################

from dash import (
    Dash, dcc, html, Input, Output, State,
    callback, page_registry, page_container
)
from flask_wtf.csrf import CSRFProtect

from app import app
from pages.layouts import get_header, get_footer
from pages.not_found_404 import layout as layout_404
from pages.home import layout as layout_home
from pages.all_dynasties.all_dynasties import layout as layout_all_dynasties
from pages.first_dynasty.first_dynasty import layout as layout_first_dynasty
from pages.second_dynasty.second_dynasty import layout as layout_second_dynasty
from pages.all_periods.all_periods import layout as layout_all_periods

import ssl
import dash
import dash_bootstrap_components as dbc
import sys
import logging
import pandas as pd

import callbacks
#import config  # necessary for future ML CV&classification feature dealing with own images

##########################
# coding
##########################

# set basic, simple console logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("pharaoh_hieroglyphs")

# create an SSL context  (future toDo: certificate and key files don't exist yet)
ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
#ssl_context.load_cert_chain(certfile='path/to/certificate.pem', keyfile='path/to/private_key.pem'

# incorporate data
try:
    logging.info("Read in egypt hieroglyphs csv file")
    df = pd.read_csv("../data/egypt_pharaohs_dynasties.csv")

    # remove empty columns
    df = df.drop(columns=['king_two_ladies', 'king_horus_gold'])

except Exception as e:
    logger.exception("Exit because exception of type %s occurred. Details: %s",
                     type(e).__name__, str(e))
    sys.exit(1)

logging.info('Dataset content overview ...\n %s \n----------', df.info())

    
def get_dynasty_names(start_no, end_no):
    ''' Returns specific dynasties from start up to end params as unique list '''
    dynasty_list = df.query('@start_no <= dynasty_no <= @end_no')['dynasty_name'].unique()
    return dynasty_list
    
first_dynasty_names = get_dynasty_names(1,9)
decimal_dynasty_names = get_dynasty_names(10,19)
twenties_dynasty_names = get_dynasty_names(20,29)


#
# app layout
#
header = get_header(first_dynasty_names, decimal_dynasty_names, twenties_dynasty_names)
footer = get_footer()
app.layout = dbc.Container(
    children =[
        dcc.Store(id="store", data={}),
        dcc.Location(id='url', refresh=False),
        header,
        #page_container,
        html.Div(id='page-content',),
        html.Hr(),
        footer,
        html.Br(),
    ],
    fluid=True,
    style={
        'background-color': '#f7f7f4',
        'background-size': '100%',
        'padding': 5,
    },
)


#
# add controls to build the interaction
#

# changes layout of the page based on the URL,
# read current URL page "http://127.0.0.1:8050/<page path - name>"
# and return associated layout
@app.callback(Output('page-content', 'children'),  #this changes the content
              [Input('url', 'pathname')])  #this listens for the url in use
def display_page(pathname):
    logger.info('--- MAIN - Selected page path: %s ---', pathname)
    
    if pathname == '/':
        return layout_home
    elif pathname == '/pages/all_periods/':
        return layout_all_periods
    elif pathname == '/pages/all_dynasties/':
        return layout_all_dynasties
    elif pathname == '/pages/first_dynasty/':
         return layout_first_dynasty
    elif pathname == '/pages/second_dynasty/':
         return layout_second_dynasty
    else:
        # domain page not found, return 404 page
        return layout_404  


#
# run the app
#
if __name__ == '__main__':
    logger.info(" ***  Start pharaoh hieroglyphs app...  *** ")
    # run on local machine with default http://127.0.0.1:8050/
    app.run(debug=True)

    # run the app on server with SSL/TLS encryption
    #app.run_server(ssl_context=ssl_context)