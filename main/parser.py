from instabot import Bot, utils
from .models import IGAccount
from main.models import Task
import datetime
from django.core.files import File


class InstagramAccount:
    def __init__(self, model=IGAccount, cooldown=0):
        self.model = model
        self.cooldown = cooldown
        delta = datetime.datetime.now() - datetime.timedelta(minutes=self.cooldown)
        self.account = self.model.objects.filter(last_use__lt=delta, in_use=False).order_by('last_use').first()
        self.username = self.account.username
        self.password = self.account.password

    def in_use(self):
        self.account.in_use = True
        self.account.save()

    def not_in_use(self):
        self.account.in_use = False
        self.account.save()


class Parser:
    def __init__(self, users, quantity, account):
        self.users = users.replace(' ', '').split(',')
        self.quantity = quantity
        self.account = account
        self.bot = Bot()
        self.followers = []
        self.bot.login(username=self.account.username, password=self.account.password)

    def parse_followers(self):
        for user in self.users:
            try:
                self.followers += self.bot.get_user_followers(user, nfollows=self.quantity)
            except Exception as e:
                print(e)
                continue
        return self.followers


class SaveTaskResult:
    def __init__(self, result, task_pk, model=Task):
        self.result = result
        self.task_pk = task_pk
        self.model = model

    def save_result(self):
        with open(f'task_{self.task_pk}.txt', 'a+') as f:
            f.write('\n'.join(self.result))
            task = Task(pk=self.task_pk)
            task.result = File(f)
            task.completed = True
            task.save()


def run_parser(users, quantity, task_pk):
    account = InstagramAccount()
    account.in_use()
    parser = Parser(users, quantity, account)
    try:
        parsed_data = parser.parse_followers()
        task_result = SaveTaskResult(parsed_data, task_pk)
        task_result.save_result()
    except Exception as e:
        print(e)
    finally:
        account.not_in_use()
    return True