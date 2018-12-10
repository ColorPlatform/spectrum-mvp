import flask
import pymongo
import argparse
import json
from color_mongo import ColorMongo

from flask import request as frequest

app = flask.Flask(__name__)



def shutdown_server():
    func = frequest.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/account/<user_id>')
def account(user_id):
    wallet = color_mongo.find_one({'key': user_id})

    if not wallet:
        return flask.Response('No such user', status=404)
    print(wallet)
    shutdown_server()
    return flask.Response(json.dumps({'key': user_id, 'value': str(wallet['value'])}), status=200)


@app.route('/transfer', methods=['POST'])
def transfer():
    from_user_id = frequest.form['from_user_id']
    to_user_id = frequest.form['to_user_id']
    amount = int(frequest.form['amount'])
    response = None

    color_mongo.start_transaction()
    sender_balance = int(color_mongo.find_one({'key': from_user_id}).get("value"))
    if sender_balance >= amount:
        remaining_amount = sender_balance - amount
        color_mongo.update_one({'key': from_user_id}, {'$set': {'value': str(remaining_amount)}})
        recipient_balance = int(color_mongo.find_one({'key': to_user_id}).get("value"))
        color_mongo.update_one({'key': to_user_id}, {'$set': {'value': str(recipient_balance + amount)}})
        response = flask.Response(json.dumps({'from_user_id': from_user_id, 'balance': remaining_amount}), status=200)
        try:
            result = color_mongo.commit_transaction()
            if result == -1:
                raise pymongo.errors.OperationFailure("something wrong shut the light")
        except pymongo.errors.OperationFailure as exc:
            response = flask.Response(json.dumps({"msg": "Lock contention"}), status=409)
    else:
        err_msg = {'msg': "Not enough founds", 'from_user_id': from_user_id, 'balance': sender_balance}
        response = flask.Response(json.dumps(err_msg), status=409)
        color_mongo.abort_transaction()
    shutdown_server()

    return response


# TODO Rewrite
@app.route('/create_wallet', methods=['POST'])
def create_wallet():
    user_id = frequest.form['user_id']
    amount = frequest.form['amount']

    wallet = {'key': user_id, 'value': amount}

    try:
        color_mongo.start_transaction()
        wallet_id = color_mongo.insert_one(wallet)
        color_mongo.commit_transaction()
    except pymongo.errors.DuplicateKeyError:
        shutdown_server()
        return flask.Response('User with this name already exist', status=409)
    shutdown_server()
    return flask.Response('Registered', status=200)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='mongo:27017', help='MongoDB URI [default: %(default)s]')
    parser.add_argument('--blockchain', default='http://localhost', help='Blockchain root URL')
    args = parser.parse_args()

    # XXX How do this work in multi-thread environment?
    color_mongo = ColorMongo(args.blockchain, args.host)

    app.run(host='0.0.0.0', port=80)
