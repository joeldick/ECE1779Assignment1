from flask import Flask

app = Flask(__name__)

from manager import monitor_pool
from manager import db
from manager import workers
from manager import loadbalancer
from manager import index
from manager import login_register
from manager import start
from manager import stop
from manager import autoscaling_policy
from manager import s3


