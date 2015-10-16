Ian Garrett
10/16/2015

# proj3-ajax
Reimplement the RUSA ACP controle time calculator with flask and ajax

## ACP controle times

That's "controle" with an 'e', because it's French, although "control" is also accepted.  Controls are points where 
a rider must obtain proof of passage, and control[e] times are the minimum and maximum times by which the rider must
arrive at the location.  

The algorithm for calculating controle times is described at http://www.rusa.org/octime_alg.html .

This project essentially replaces the calculator at http://www.rusa.org/octime_acp.html .

## AJAX and Flask reimplementation

We have to catch certain exceptions in checkpoint distance when calculating opening and closing times.

When a checkpoint distance was up to but no more then 20% greater than the brevet distance, the open and closing times were fixed at what they were calculated at when the checkpoint is EQUAL to the brevet date. However, for certain brevet distances we have to add either 10 or 20 minutes to the closing time. If the brevet distance was set to either 200 or 1,000, we add 10 minutes to the closing time If the brevet distance was set to 400, we add 20 minutes to the closing time.



## requirements.txt
Flask==0.10.1
Jinja2==2.8
MarkupSafe==0.23
Werkzeug==0.10.4
arrow==0.6.0
itsdangerous==0.24
python-dateutil==2.4.2
six==1.10.0


## Testing

A requirement of this project will be designing a systematic test suite. 
