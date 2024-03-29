# Copyright 2012, Cercle Informatique. All rights reserved.

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from getpass import getpass, getuser
from category.models import Category, CategoryItem
from group.models import Group
from course.models import Course, CourseInfo
from optparse import make_option
from message.models import Thread, Message
from preference.models import Shortcut


class Command(BaseCommand):
    help = 'Initialize fognar for developpment'
    option_list = BaseCommand.option_list + (
        make_option('--username', action='store', dest='username', default=None, help='default username'),
        make_option('--password', action='store', dest='password', default=None, help='default password'),
        make_option('--first-name', action='store', dest='first_name', default=None, help='default first name'),
        make_option('--last-name', action='store', dest='last_name', default=None, help='default last name'),
        )

    def handle(self, *args, **options):
        self.stdout.write('Creating user\n')
        user = User()
        username = raw_input("Username (default: %s): " % getuser()) if options["username"] is None else options["username"]
        if not username:
            username = getuser()
        user.username = username
        password = getpass("Password (default: 'test'): ") if options["password"] is None else options["password"]
        if not password:
            password = 'test'
        first_name = raw_input("Firstname (default: John): ") if options["first_name"] is None else options["first_name"]
        if not first_name:
            first_name = "John"
        last_name = raw_input("Lastname (default: Smith): ") if options["last_name"] is None else options["last_name"]
        if not last_name:
            last_name = "Smith"
        user.first_name = first_name
        user.last_name = last_name
        user.set_password(password)
        user.save()
        profile = user.get_profile()
        profile.name = first_name + " " + last_name
        profile.email = '42@urlab.be'
        profile.save()

        self.stdout.write('Adding base data ...\n')
        c1 = Course.objects.create(slug='info-f-666', name='Hell Informatique',
                                   description='Hell Computer Science course')
        c2 = Course.objects.create(slug='info-f-777', name='Over Math',
                                   description='New math course based on fuzzy axiomes')
        c3 = Course.objects.create(slug='info-f-888', name='AlgoSimplex',
                                   description='Les simplex dans tout leurs etats')
        c4 = Course.objects.create(slug='info-f-999', name='Support Vector Machines',
                                   description='Neural Networks are outdated, use SVM!')

        i1 = CourseInfo.objects.create(user=profile,
                                       infos = """[
            {    name: "general", values: [
                                        {name: 'Professeur', value:'B. Lecharlier'},
                                        {name: 'Langue', value:'Francais'},
                                        {name: 'Syllabus', value:'Informatique Ba1'},
                                        {name: 'ECTS', value:'5'},
                                    ],
            },
        ]""")

        i2 = CourseInfo.objects.create(user = profile,
                                       prev=i1,
                                       infos = """[
            {    name: "general", values: [
                                        {name: 'Professeur', value:'B. Lecharlier'},
                                        {name: 'Langue', value:'Francais'},
                                        {name: 'Syllabus', value:'Informatique Ba1'},
                                        {name: 'ECTS', value:'5'},
                                    ],
            },
            {    name: "exam", values: [
                                      {name: 'Difficultes', values:'Language noyaux'},
                                     ],
            },
        ]""")
        c1.infos = i2
        c1.save()

        g1 = Group.objects.create(slug='CI', name='Cercle Informatique',
                                  description='Cercle des etudiants en info \o/')
        g2 = Group.objects.create(slug='ACE', name='Association des Cercles Etudiants',
                                  description='Youplaboom')

        Shortcut.objects.create(user=profile, position=1, app="course", app_id=c1.id)
        Shortcut.objects.create(user=profile, position=2, app="course", app_id=c2.id)
        Shortcut.objects.create(user=profile, position=3, app="course", app_id=c3.id)
        Shortcut.objects.create(user=profile, position=4, app="course", app_id=c4.id)
        Shortcut.objects.create(user=profile, position=5, app="group", app_id=g1.id)
        Shortcut.objects.create(user=profile, position=6, app="group", app_id=g2.id)

        cat0 = Category.objects.create(name='Faculty', description='Root node w/ category')
        cat1 = Category.objects.create(name='Sciences', description='Fac de sciences')
        cat2 = Category.objects.create(name='Polytech', description='Polytech')
        cat3 = Category.objects.create(name='Informatique', description='Section INFO')

        cat0.holds.add(cat1)
        cat0.holds.add(cat2)
        cat1.holds.add(cat3)

        CategoryItem.objects.create(category=cat3, thing=c1, priority=1)
        CategoryItem.objects.create(category=cat3, thing=c2, priority=2)
        CategoryItem.objects.create(category=cat3, thing=c4, priority=3)
        CategoryItem.objects.create(category=cat3, thing=g1, priority=3)
        CategoryItem.objects.create(category=cat0, thing=g2, priority=1)
        CategoryItem.objects.create(category=cat2, thing=c3, priority=1)

        thread = Thread.objects.create(user=User.objects.all()[0].profile, refer_content=ContentType.objects.get_for_model(Course), refer_oid=c1.id, subject="A JSON stringifier goes in the opposite direction, converting JavaScript data structures into JSON text. JSON does not support cyclic data structures, so be careful to not give cyclical structures to the JSON stringifier. http://www.json.org/js.html", category="info pratique")
        Message.objects.create(user=user.get_profile(), thread=thread, text='Type "copyright", "credits" or "license" for more information.')
