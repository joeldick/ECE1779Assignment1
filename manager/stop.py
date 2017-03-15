from flask import render_template, redirect, url_for
from manager import app, loadbalancer

import boto3


@app.route('/stop')
def stop():
    # clean up
    ec2 = boto3.resource('ec2')
    elb = boto3.client('elb')

    elb.delete_load_balancer(LoadBalancerName=loadbalancer.elb_name)
    all_ec2_instances = ec2.instances.all()
    for instance in all_ec2_instances:
        if instance.tags is not None:
            for tag in instance.tags:
                if tag['Key'] == 'Role' \
                        and tag['Value'] == 'worker' \
                        and instance.state.get('Name') == 'running':
                    instance.terminate()
                    break

    return redirect(url_for('index'))
