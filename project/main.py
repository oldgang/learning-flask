from flask import Blueprint, Flask, render_template, redirect, url_for, request, session, flash
from flask_login import login_required, current_user
from .lte import is_valid_ipv4, fetch_lte_usage, fetch_lte_stats
from . import db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('index.html')
    return redirect(url_for('auth.login'))

@main.route('/graphs')
@login_required
def graphs():
    return render_template('graphs.html')

@main.route('/lteTransfer')
@login_required
def lteTransfer():
    return render_template('lteTransfer.html')

@main.route('/lteTransfer/', methods=['POST'])
@login_required
def calculateLteTransfer():
        ip = request.form['lteTextInput']
        if not is_valid_ipv4(ip):
                return render_template('lteTransfer.html', text='Niepoprawny adres IP')
        
        data = fetch_lte_usage(ip)

        if data == None:
                return render_template('lteTransfer.html', text='Nie można połączyć się z urządzeniem')
        
        daily = f"{data['dailyGigabytes']} GB"
        weekly = f"{data['weeklyGigabytes']} GB"
        monthly = f"{data['monthlyGigabytes']} GB"
        yearly = f"{data['yearlyGigabytes']} GB"

        stats = fetch_lte_stats(ip)
        print(stats)

        return render_template('lteTransfer.html', text='', usage=[daily, weekly, monthly, yearly], ip=ip, stats=stats)