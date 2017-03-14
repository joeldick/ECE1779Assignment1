from flask import render_template, redirect, url_for
from manager import app

import boto3
import time
from manager import db
from manager import worker
from manager import loadbalancer


@app.route('/start')
def start():
    # create ec2 resource
    ec2 = boto3.resource('ec2')

    # create database server
#    db_instance = db.create_ec2_database()[0]
    # wait for db server instance to be running so we're sure we can get the public dns
#    time.sleep(1)
#    while list(ec2.instances.filter(InstanceIds=[db_instance.id]))[0].state.get('Name') != 'running':
#    time.sleep(0.1)
    sql_host = db.db_config.get('host')


    # create first worker instance, passing in the name of the db server hostname
    worker1_instance = worker.create_ec2_worker(sql_host=sql_host)[0]
    time.sleep(1)
    while list(ec2.instances.filter(InstanceIds=[worker1_instance.id]))[0].state.get('Name') != 'running':
        time.sleep(0.1)
    worker_host = list(ec2.instances.filter(InstanceIds=[worker1_instance.id]))[0].public_dns_name
    print('worker up and running on: ' + worker_host + ':5000')

    # create load balancer
    elb = boto3.client('elb')
    loadbalancer.create_loadbalancer()
    elb_description = elb.describe_load_balancers(LoadBalancerNames=[loadbalancer.elb_name])
    loadbalancer_host = elb_description.get('LoadBalancerDescriptions')[0].get('DNSName')
    print('load balancer up and running on: ' + loadbalancer_host)

    # regester first worker instance with load balancer
    elb.register_instances_with_load_balancer(LoadBalancerName=loadbalancer.elb_name,
                                              Instances=[{
                                                  'InstanceId': worker1_instance.id
                                              }]
                                              )

    return render_template("admin/start.html",
                           page_header="Start complete",
                           sql_host=sql_host,
                           worker1_host=worker_host + ':5000',
                           loadbalancer_host=loadbalancer_host
                           )

@app.route('/start_sql')
def start_sql():
    db.create_ec2_database()
    return redirect(url_for('index'))
