from os import environ

import requests
from flask import abort, Flask, request

application = app = Flask(__name__)

slack = requests.Session()
slack.params.update({
    'token': environ['SLACK_API_TOKEN'],
})
slack_slash_command_token = environ['SLACK_SLASH_COMMAND_TOKEN']
slack_users = {
    user['id']: user for user in
    slack.get('https://slack.com/api/users.list').json()['members']
}

deploybot = requests.Session()
deploybot.headers.update({
    'X-Api-Token': environ['DEPLOYBOT_API_TOKEN'],
})
deploybot_subdomain = environ['DEPLOYBOT_SUBDOMAIN']
deploybot_users = {
    user['email']: user for user in
    deploybot.get(
        'https://{}.deploybot.com/api/v1/users'.format(deploybot_subdomain),
    ).json()['entries']
}


@app.route('/', methods=['POST'])
def handler():
    if request.form['token'] != slack_slash_command_token:
        abort(403)
    slack_user = slack_users[request.form['user_id']]
    args = request.form['text'].split()
    command = args.pop(0)

    if command == 'environments':
        environments = [
            """*{name}*
ID: {id}
Current version: {current_version}
Branch: {branch_name}
""".format(**env) for env in
            deploybot.get(
                'https://{}.deploybot.com/api/v1/environments'.format(deploybot_subdomain),
            ).json()['entries']
        ]
        return '\n\n'.join(environments)

    return """Available commands:
*environments* - _Lists environments_
"""


if __name__ == '__main__':
    app.run(debug=True)
