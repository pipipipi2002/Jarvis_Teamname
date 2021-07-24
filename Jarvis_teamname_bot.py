"""use the token below for better access! Search for @Jarvis_TeamNamebot. use google collab for easier setup"""

# pip install python-telegram-bot

#!/usr/bin/env python
import logging
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)
from telegram import ReplyKeyboardMarkup, Update, ReplyKeyboardRemove

# INSERT TOKEN HERE. will remove my token in 26/7/21
TOKEN = "1927044960:AAF58humxeEAF2_ajP3SeT5djqn-XyTCHvE"

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


# Conversation Handler Range setter
CHOOSING, CLASS_NAME, S_CHOOSE_CLASS = range(3)
CHOOSING_CLASS, WRITING_TITLE, WRITING_DEADLINE, WRITING_DESC, CONFIRM = range(5)
CHOOSE_TYPE, TYPE_CLASSMEMBERS_CLASS, TYPE_ASSIGNMENTS_CLASS = range(3)
DELETE_CLASS, DELETE_CLASS_AID, CONFIRMATION = range(3)
# Class Database
CLASSROOMS = {}
MESSAGE_SESSION = {}



class Create_classroom:
    def __init__(self, tchat_id, tusername):
        self.tchat_id = tchat_id
        self.tusername = tusername

    def make_classroomObj(self):
        json_data = {
            "teacher": {
                "chat_id": self.tchat_id,
                "username": self.tusername
            },
            "students": {},
            "assignments":{},
            "assignment_count":0
        }
        return json_data

# Basic command handler
def start_command(update, context):
    update.message.reply_text(
      "I am Jarvis, your personal learning and teaching assistant.\n"  
      "How may i be of help?\n"
      "Type /help for more information",
      parse_mode = "HTML"
  )

def help_command(update, context):
    user = update.message.from_user.username
    update.message.reply_text(
        f"Hello {user}! I am Jarvis, your personal learning and teaching assistant.\n"
        "I can do all these things:\n\n"
        "<b>General Commands</b>\n"
        "/start : Wake me up!\n"
        "/help : Stuck? Call me for help with this command\n"
        "/view : View your classes, classmates and assignments\n"
        "/reg : Join classes as a student or form classes as a teacher\n\n"
        "<b>Teacher Commands</b>\n"
        "/new : add new assignments to your class\n"
        "/del : delete assignment you assigned\n",
        parse_mode = "HTML"
    )


# Register commands
def register_command(update, context):
    reply_keyboard = [['Teacher', 'Student'],['Cancel']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, input_field_placeholder='Teacher or Student?')
    update.message.reply_text(
        "Please choose your role : ",
        reply_markup=markup,
    )
    return CHOOSING

def teacher_registration(update, context):
    # register class name and attach teacher id to the class
    update.message.reply_text("You will be registering a new class. Please enter the Class Name: ", reply_markup=ReplyKeyboardRemove(),)
    return CLASS_NAME

def className_registration(update, context):
    global CLASSROOMS
    class_name = update.message.text
    teacher_id = update.message.from_user.id
    teacher_username = update.message.from_user.username

    # Create a classroom object
    newClass = Create_classroom(teacher_id, teacher_username)
    json_data = newClass.make_classroomObj();

    # append the new class into classroom database
    CLASSROOMS[class_name] = json_data

    update.message.reply_text(f"Class <b>{class_name}</b> successfully registered.", parse_mode="HTML")
    return ConversationHandler.END

def student_registration(update, context):
    keyboard = [['Cancel']]
    class_list = CLASSROOMS.keys()

    for item in class_list:
        keyboard.append([item])

    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, input_field_placeholder='Choose Class')    
    update.message.reply_text("Choose a class to register!", reply_markup=markup)
    return S_CHOOSE_CLASS


def student_regis_class(update, context):
    global CLASSROOMS 
    # check if class is in classroom database
    chosen_class = update.message.text
    if chosen_class not in CLASSROOMS:
        update.message.reply_text(
            "<b>Class not registered in database.</b>",
            parse_mode = "HTML", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    # check if the student is a teacher of that class
    student_chatId = update.message.from_user.id
    if student_chatId == CLASSROOMS[chosen_class]["teacher"]["chat_id"]:
        update.message.reply_text(
            "<b>You are a teacher of this class. You cannot register as a student</b>",
            parse_mode = "HTML", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    # check if the student is already in the class
    if student_chatId in CLASSROOMS[chosen_class]["students"].values():
        update.message.reply_text(
            "<b>You already a student of this class.</b>",
            parse_mode = "HTML", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    student_username = update.message.from_user.username

    CLASSROOMS[chosen_class]["students"][f"{student_username}"] = student_chatId
    update.message.reply_text(
        f"Student <b>{student_username}</b> successfully registered to class <b>{chosen_class}</b>.",
        parse_mode="HTML", reply_markup=ReplyKeyboardRemove()
        )
    return ConversationHandler.END

def cancel_registration(update, context):
    update.message.reply_text("Registration Cancelled", reply_markup=ReplyKeyboardRemove(),)
    return ConversationHandler.END

# View commands
def view_command(update, context):
    class_list = CLASSROOMS.keys()
    if len(class_list) == 0:
        update.message.reply_text(
            "There are no registered classrooms in the database"
            "Please register one using the /register command", 
            parse_mode="HTML")
        return ConversationHandler.END
    reply_keyboard = [['Class', 'Class Members', 'Assignments'],['Cancel']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, input_field_placeholder='What do you want to view?')
    update.message.reply_text(
        "What would like to view?",
        reply_markup=markup
    )
    return CHOOSE_TYPE

def type_class(update, context):
    chat_id = update.message.from_user.id
    class_list = CLASSROOMS.keys()
    message = f"There are {len(class_list)} class(es) available:\n"
    # check if user is teacher or student
    for klass in class_list:
        teacher_id = CLASSROOMS[klass]["teacher"]["chat_id"]
        student_ids = CLASSROOMS[klass]["students"].values()

        if chat_id == teacher_id:
            message += f"    - {klass} as <b>Teacher</b>\n"
        elif chat_id in student_ids:
            message += f"    - {klass} as <b>Student</b>\n"
        else:
            message += f"    - {klass} <i>Not Enrolled</i>\n"

    update.message.reply_text(message, parse_mode="HTML", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def type_classmembers(update, context):
    keyboard = [['Cancel']]
    class_list = CLASSROOMS.keys()

    for item in class_list:
        keyboard.append([item])

    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, input_field_placeholder='Choose Class')    
    update.message.reply_text("Choose a class to view their members!", reply_markup=markup)
    return TYPE_CLASSMEMBERS_CLASS

def type_classmembers_class(update, context):
    # check input with database
    chosen_class = update.message.text
    if chosen_class not in CLASSROOMS:
        update.message.reply_text(
            "<b>Class not registered in database.</b>",
            parse_mode = "HTML", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    message = f"The members of the class {chosen_class} are: \n"
    teacher_name = CLASSROOMS[chosen_class]["teacher"]["username"]
    student_names = CLASSROOMS[chosen_class]["students"].keys()

    message += f"Teacher: {teacher_name}\nWith {len(student_names)} student(s):\n"

    for student in student_names:
        message += f"  - {student}\n"

    update.message.reply_text(message, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def type_assignments(update, context):
    keyboard = [['Cancel']]
    class_list = CLASSROOMS.keys()

    for item in class_list:
        keyboard.append([item])

    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, input_field_placeholder='Choose Class')    
    update.message.reply_text("Choose a class to view their assignments!", reply_markup=markup)
    return TYPE_ASSIGNMENTS_CLASS

def type_assignments_class(update, context):
    # check input with database
    chosen_class = update.message.text
    if chosen_class not in CLASSROOMS:
        update.message.reply_text(
            "<b>Class not registered in database.</b>",
            parse_mode = "HTML", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    assignments_obj = CLASSROOMS[chosen_class]["assignments"]

    message = f"There are {len(assignments_obj)} assignment(s) for class <b>{chosen_class}</b>:\n"
    for assignment in assignments_obj.values():
        message += f" - {assignment['title']} (AID: {assignment['id']})\n"
        message += f"    =&gt By: <i>{assignment['deadline']}</i>\n"
        message += f"    =&gt Desc: {assignment['desc']}\n"

    update.message.reply_text(message, parse_mode="HTML",reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def cancel_v(update, context):
    update.message.reply_text(
        'View Cancelled',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

# ADD Assignments Command
def addNew_a(update, context):
    # class list from the CLASSROOMS database
    class_list = CLASSROOMS.keys()
    if len(class_list) == 0:
        update.message.reply_text(
            "There are no registered classrooms in the database"
            "Please register one using the /register command", 
            parse_mode="HTML")
        return ConversationHandler.END

    keyboard = []
    for item in class_list:
        keyboard.append([item])
    keyboard.append(['Cancel'])

    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, input_field_placeholder='Choose Class')
    update.message.reply_text(
        "Please choose the class you want to send new assignments to!  ",
        reply_markup=markup,
    )
    return CHOOSING_CLASS

def chosenClass_a(update, context):
    # check class in database
    chosen_class = update.message.text
    if chosen_class not in CLASSROOMS:
        update.message.reply_text(
            "<b>Class not registered in database.</b>"
            "You cannot add new assignments",
            parse_mode = "HTML", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    # Check whether you are the teacher
    user_chatid = update.message.from_user.id
    if CLASSROOMS[chosen_class]["teacher"]["chat_id"] != user_chatid:
        update.message.reply_text(
            "<b>You are not the teacher for this class.</b>"
            "You cannot add new assignments",
            parse_mode = "HTML", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    context.user_data['class_a'] = chosen_class
    context.user_data['title_a'] = ''
    context.user_data['deadline_a'] = ''
    context.user_data['desc_a'] = ''

    update.message.reply_text(
        f"Class <b>{update.message.text}</b> choosen.\n"
        "What is the title of this new assignment?\n"
        "Type '<i>Cancel</i>' to cancel",
        reply_markup=ReplyKeyboardRemove(), parse_mode="HTML")


    return WRITING_TITLE

def chosenTitle_a(update, context):
    title = update.message.text
    context.user_data['title_a'] = title
    
    update.message.reply_text(
        "When is the assignment due?\n"
        "Type '<i>Cancel</i>' to cancel",
        parse_mode="HTML")
    return WRITING_DEADLINE

def chosenDeadline_a(update, context):
    deadline = update.message.text
    context.user_data['deadline_a'] = deadline
    update.message.reply_text(
        "Please write some description of the assignment here.\n"
        "Type '<i>Cancel</i>' to cancel",
        parse_mode="HTML")
    return WRITING_DESC

def chosenDesc_a(update, context):
    desc = update.message.text
    context.user_data['desc_a'] = desc

    reply_keyboard = [['Correct','Cancel']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

    update.message.reply_text(
        f"The assignment details are as follows:\n"
        f"Title : {context.user_data['title_a']}\n"
        f"Deadline : {context.user_data['deadline_a']}\n"
        f"Description : {context.user_data['desc_a']}\n"
        "Is this correct?",
        reply_markup=markup
        )

    return CONFIRM
def confirm_a(update, context):
    update.message.reply_text("Assignment created.\nSending to students...", reply_markup=ReplyKeyboardRemove(),)
    global CLASSROOMS
    global MESSAGE_SESSION
    chosenClass_a = context.user_data['class_a']
    CLASSROOMS[chosenClass_a]["assignment_count"] += 1
    id = CLASSROOMS[chosenClass_a]["assignment_count"]
    context.user_data["AID_input"] = id
    assignment_dict = {
        "id": id,
        "title": context.user_data['title_a'],
        "deadline": context.user_data['deadline_a'],
        "desc": context.user_data['desc_a']
    }    

    CLASSROOMS[chosenClass_a]["assignments"][id] = assignment_dict

    chat_id = update.message.from_user.id
    MID = send_message_to_students(context, chosenClass_a, assignment_dict, "sent a new")
    message_text = f"Successful, {len(CLASSROOMS[chosenClass_a]['students'])} student(s) received the message on <b>ADDING assignment {assignment_dict['title']}</b>.\nStudents acknowledged:\n"
    message = update.message.reply_text(message_text, parse_mode="HTML",reply_markup=ReplyKeyboardRemove())
    messageSession = Message_session(chat_id, message.message_id, message_text, MID)
    data = messageSession.toJson()
    MESSAGE_SESSION[MID] = data

    return ConversationHandler.END

def cancel_a(update, context):
    del context.user_data['class_a']
    del context.user_data['title_a']
    del context.user_data['deadline_a']
    del context.user_data['desc_a']

    update.message.reply_text("Assignment not created", reply_markup=ReplyKeyboardRemove(),)
    return ConversationHandler.END

# DELETE / CANCEL the assignment
def delete_a(update, context):
    # choose class
    class_list = CLASSROOMS.keys()
    if len(class_list) == 0:
        update.message.reply_text(
            "There are no registered classrooms in the database"
            "Please register one using the /register command", 
            parse_mode="HTML")
        return ConversationHandler.END

    keyboard = []
    for item in class_list:
        keyboard.append([item])
    keyboard.append(['Cancel'])

    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, input_field_placeholder='Choose Class')
    update.message.reply_text(
        "Please choose the class you want to delete the assignments from!  ",
        reply_markup=markup,
    )
    return DELETE_CLASS

def delete_class(update, context):
    # check class in database
    chosen_class = update.message.text
    if chosen_class not in CLASSROOMS:
        update.message.reply_text(
            "<b>Class not registered in database.</b>"
            "You cannot delete assignments",
            parse_mode = "HTML", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    # Check whether you are the teacher
    user_chatid = update.message.from_user.id
    if CLASSROOMS[chosen_class]["teacher"]["chat_id"] != user_chatid:
        update.message.reply_text(
            "<b>You are not the teacher for this class.</b>"
            "You cannot delete assignments",
            parse_mode = "HTML", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    # check if there are assignments in the class
    assignments_obj = CLASSROOMS[chosen_class]["assignments"]
    if len(assignments_obj) == 0:
        update.message.reply_text(
            f"No assignments in class <b>{chosen_class}</b>",
            parse_mode="HTML", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    # Display the current assignments
    message = f"There are {len(assignments_obj)} assignment(s) for class <b>{chosen_class}</b>:\n"
    for assignment in assignments_obj.values():
        message += f" - {assignment['title']} (AID: {assignment['id']})\n"
        message += f"    =&gt By: <i>{assignment['deadline']}</i>\n"
        message += f"    =&gt Desc: {assignment['desc']}\n"

    update.message.reply_text(message, parse_mode="HTML",reply_markup=ReplyKeyboardRemove())
    
    # collate Assignment ID
    AID = []
    for assignment in assignments_obj.values():
        AID.append(assignment["id"])

    context.user_data["AID"] = AID
    context.user_data["chosen_class"] = chosen_class
    context.user_data["assignments_obj"] = assignments_obj
    update.message.reply_text(
        f"Select the assignment's AID to remove from class <b>{chosen_class}</b>\n"
        "Please insert numbers only or type <i>Cancel</i> to cancel",
        parse_mode="HTML")
    return DELETE_CLASS_AID
    
def delete_class_aid(update, context):
    #check aid is present in the AID list
    AID = context.user_data["AID"]
    AID_input = int(update.message.text)
    if AID_input not in AID:
        update.message.reply_text(
            f"{AID_input} not in the list.\n" 
            "Please choose again, or type <i>Cancel</i> to cancel",
            parse_mode="HTML")
        return DELETE_CLASS_AID

    # Extract assignment information using AID
    chosen_class = context.user_data["chosen_class"]
    assignments_obj = context.user_data["assignments_obj"]
    assignment_selected = {}
    
    for assignment in assignments_obj.values():
        if assignment["id"] == AID_input:
            assignment_selected = assignment
            break

    context.user_data["AID_input"] = AID_input
    context.user_data["assignment_selected"] = assignment_selected

    # Proceed with confirmation message
    message = f"You will be deleting this assignment from class <b>{chosen_class}</b>:\n"
    message += f" - {assignment_selected['title']} (AID: {assignment_selected['id']})\n"
    message += f"    =&gt By: <i>{assignment_selected['deadline']}</i>\n"
    message += f"    =&gt Desc: {assignment_selected['desc']}\n"
    message += "Yes or No?"
    keyboard = [["Yes", "No, Choose again", "Cancel Delete"]]
    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    update.message.reply_text(message, reply_markup=markup, parse_mode="HTML")
    return CONFIRMATION

def confirmation(update, context):
    confirm = update.message.text
    if confirm == "Cancel Delete":
        del context.user_data["AID"]
        del context.user_data["chosen_class"]
        del context.user_data["assignments_obj"]
        del context.user_data["AID_input"]
        del context.user_data["assignment_selected"]
        update.message.reply_text("Delete cancelled")
        return ConversationHandler.END
    if confirm == "No, Choose again":
        del context.user_data["AID_input"]
        del context.user_data["assignment_selected"]
        message = f"Please choose another AID or type <i>Cancel</i> to cancel"
        update.message.reply_text(message, parse_mode="HTML")
        return DELETE_CLASS_AID
    chosen_class = context.user_data["chosen_class"]
    AID_input = context.user_data["AID_input"]
    assignment_selected = context.user_data["assignment_selected"]
    
    global CLASSROOMS
    global MESSAGE_SESSION
    del CLASSROOMS[chosen_class]["assignments"][AID_input]
    update.message.reply_text(f"Assignment ID {AID_input} deleted.\nSending to students...")

    #send to students
    chat_id = update.message.from_user.id
    MID = send_message_to_students(context, chosen_class, assignment_selected, "deleted an")
    message_text = f"Successful, {len(CLASSROOMS[chosen_class]['students'])} student(s) received the message on <b>DELETING AID {AID_input}</b>.\nStudents acknowledged:\n"
    message = update.message.reply_text(message_text, parse_mode="HTML", reply_markup=ReplyKeyboardRemove())
    messageSession = Message_session(chat_id, message.message_id, message_text, MID) 
    data = messageSession.toJson()
    MESSAGE_SESSION[MID] = data

    del context.user_data["AID"]
    del context.user_data["chosen_class"]
    del context.user_data["assignments_obj"]
    del context.user_data["AID_input"]
    del context.user_data["assignment_selected"]
    return ConversationHandler.END

def cancel_d(update, context):
    update.message.reply_text('Delete cancelled')
    return ConversationHandler.END

class Message_session:
    def __init__(self, tchat_id, tmessage_id, text, MID):
        self.tchat_id = tchat_id
        self.tmessage_id = tmessage_id
        self.text = text
        self.MID = MID

    def toJson(self):
        json_data = {
            'chat_id': self.tchat_id,
            'message_id': self.tmessage_id,
            'text': self.text
        }
        return json_data

"""Command to send to student"""
def send_message_to_students(context, chosenClass, dict_a, action):
    verb =""
    if (action == "deleted an"):
        verb = "DEL"
    else:
        verb = "ADD"
    student_chatIds = CLASSROOMS[chosenClass]["students"].values()
    teacher = CLASSROOMS[chosenClass]["teacher"]["username"]
    AID = str(context.user_data["AID_input"])
    
    MID = f"{chosenClass}_{AID}_{verb}"
    message = f"Teacher {teacher} from class {chosenClass} has {action} assignment\nThe assignment details are as follows:\n    Title : {dict_a['title']}\n    Deadline : {dict_a['deadline']}\n    Description : {dict_a['desc']}\n    MID : {MID}\n type '/OK <MID>' to confirm."

    keyboard = [[f"/OK {MID}"]]
    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    for chat_id in student_chatIds:
        context.bot.send_message(
        chat_id=chat_id,
        text=message,
        reply_markup = markup
    )
    return MID

def ok_command(update, context):
    global MESSAGE_SESSION
    text = update.message.text.split(" ")
    if len(text) == 1:
        update.message.reply_text(f"Invalid Message ID (MID). Acknowledgment failed. Check again.")
    MID = text[1:]
    session = MESSAGE_SESSION[MID]
    student_username = update.message.from_user.username

    message = session["text"]
    message += f"  - {student_username}\n"

    MESSAGE_SESSION[MID]["text"] = message

    context.bot.edit_message_text(
        text=message,
        chat_id=session['chat_id'],
        message_id=session['message_id']
    )
    update.message.reply_text(f"{MID} Acknowledged!")


# Error handler callback
def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)    

def main():
    """Run the Bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add Command Handlers
    dp.add_handler(CommandHandler('start', start_command))
    dp.add_handler(CommandHandler('help', help_command))  
    dp.add_handler(CommandHandler('OK', ok_command))


    # Add Conversation Handlers 
    conv_handler_register = ConversationHandler(
        entry_points=[CommandHandler('reg', register_command)],
        states={
            CHOOSING: [
                MessageHandler(Filters.regex('^Teacher$'), teacher_registration),
                MessageHandler(Filters.regex('^Student$'), student_registration)
            ],
            CLASS_NAME: [MessageHandler(Filters.text & ~Filters.command, className_registration)],
            S_CHOOSE_CLASS: [MessageHandler(Filters.text & ~Filters.regex('^Cancel$'), student_regis_class)]            
        },
        fallbacks=[MessageHandler(Filters.regex('^Cancel'), cancel_registration)]
    )
    conv_handler_addAssignments = ConversationHandler(
        entry_points=[CommandHandler('new', addNew_a)],
        states={
            CHOOSING_CLASS: [MessageHandler(Filters.text & ~Filters.regex('^Cancel$'), chosenClass_a)],
            WRITING_TITLE: [MessageHandler(Filters.text & ~Filters.regex('^Cancel$') & ~Filters.command, chosenTitle_a)],
            WRITING_DEADLINE: [MessageHandler(Filters.text & ~Filters.regex('^Cancel$')& ~Filters.command, chosenDeadline_a)],
            WRITING_DESC: [MessageHandler(Filters.text & ~Filters.regex('^Cancel$')& ~Filters.command, chosenDesc_a)],
            CONFIRM: [MessageHandler(Filters.regex('^Correct$') & ~Filters.regex('^Cancel$')& ~Filters.command, confirm_a)]
        },
        fallbacks=[MessageHandler(Filters.regex('^Cancel'), cancel_a)]
    )
    conv_handler_view = ConversationHandler(
        entry_points=[CommandHandler('view', view_command)],
        states={
            CHOOSE_TYPE: [
                MessageHandler(Filters.regex('^Class$'), type_class),
                MessageHandler(Filters.regex('^Class Members$'), type_classmembers),
                MessageHandler(Filters.regex('^Assignments$'), type_assignments)
                ],
            TYPE_CLASSMEMBERS_CLASS: [
                MessageHandler(Filters.text & ~Filters.regex('^Cancel$') & ~Filters.command, type_classmembers_class)
            ],
            TYPE_ASSIGNMENTS_CLASS: [
                MessageHandler(Filters.text & ~Filters.regex('^Cancel$') & ~Filters.command, type_assignments_class)
            ]          
        },
        fallbacks=[MessageHandler(Filters.regex('^Cancel$'), cancel_v)]
    )
    conv_handler_delete = ConversationHandler(
        entry_points=[CommandHandler("del", delete_a)],
        states={
            DELETE_CLASS: [
                MessageHandler(Filters.text & ~Filters.regex('^Cancel$') & ~Filters.command, delete_class)
            ],
            DELETE_CLASS_AID: [
                MessageHandler(Filters.regex('^[0-9]*$') & ~Filters.regex('^Cancel$') & ~Filters.command, delete_class_aid)
            ],
            CONFIRMATION: [
                MessageHandler(Filters.regex('^(Cancel Delete|No, Choose again|Yes)$') & ~Filters.regex('^Cancel$') & ~Filters.command, confirmation)
            ]
        },
        fallbacks=[MessageHandler(Filters.regex('^Cancel$'), cancel_d)]
    )
    dp.add_handler(conv_handler_register)
    dp.add_handler(conv_handler_addAssignments)
    dp.add_handler(conv_handler_view)
    dp.add_handler(conv_handler_delete)
    # Log all errors
    dp.add_error_handler(error)

    # Start the bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == "__main__":
    main()