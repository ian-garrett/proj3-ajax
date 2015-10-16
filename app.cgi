#! /usr/bin/env python3

""" For deployment on ix under CGI """

import site
site.addsitedir("/home/faculty/michal/public_html/htbin/cis322/proj2-flask/env/lib/python3.4/site-packages")

from wsgiref.handlers import CGIHandler
from syllabus import app

CGIHandler().run(app)
