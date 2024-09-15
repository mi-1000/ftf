# Help guide

## How to know which terminal language I am using?
- In this guide, I will show commands for 3 languages, CMD, PowerShell and Bash:
  - CMD is used on Windows. It's less powerful than PowerShell, I personally don't like it, but it's totally okay for what we do. You should know you are using CMD if typing the command `ls` gives you an error.
  - PowerShell is the newer terminal language used by Windows. It is the default language in the terminal integrated to VS Code. It supports autocompletion using <kbd>TAB</kbd>.
  - Bash is used on MacOS and Linux. You can also technically run it natively on Windows through WSL, but if you know how to do that, you probably don't need this guide.

## Useful terminal commands

- Change directory:
  - CMD/PowerShell/Bash: `cd <path_to_new_directory>` - Tip: `./` is your current folder, `../` is your parent folder.
- List files in directory:
  - CMD: `dir`
  - PowerShell/Bash: `ls` - Tip: You can apply filters, for example, running `ls *.py` lists Python files only, `ls -dir d*` in PowerShell lists all subfolders whose name start with a `d`.
- Copy a file:
  - CMD: `copy <source> <destination>` - Example: `copy test.py ../file.py` copies `test.py` from your current folder into the parent folder and renames the copied file as `file.py`
  - PowerShell/Bash: `cp <source> <destination>`
- Move a file:
  - CMD: `move <source> <destination>`
  - PowerShell/Bash: `mv <source> <destination>` - Tip: You can also rename a file by moving it into the same folder, but with a different name: `mv test.py file.py` renames `test.py` to `file.py`
- Create a file:
  - CMD: `type NUL > <file_name>` (that's why I don't like CMD)
  - PowerShell: `ni <file_name>`
  - Bash: `touch <file_name>`
- Delete a file:
  - CMD: `del <file_name>` - Note: This deletes the file permanently without moving it to the recycle bin (that's also true for both other languages)
  - PowerShell/Bash: `rm <file_name>`
- Display the content of a file:
  - CMD: `type <file_name>`
  - PowerShell/Bash: `cat <file_name>`
- Create a new folder:
  - CMD/PowerShell/Bash: `mkdir <folder_name>`
- Remove an empty folder:
  - CMD/PowerShell/Bash: `rmdir <folder_name>` - Note: This removes the folder permanently, same as above with `del`/`rm`
- Remove a folder and all files inside:
  - CMD: `rd/s/q <folder_name>` - Note: I've already said it, but this removes all the files permanently without any possible backup. Same applies for both other languages.
  - PowerShell: `rm -Recurse -Force <folder_name>` - Note: That's long to type, so don't forget to use autocompletion with <kbd>TAB</kbd>.
  - Bash: `rm -r <folder_name>` - Note: You can use the flag `-f` (`rm -rf`) to bypass warnings or errors, but use it at your own risk. Typing `rm -rf /` by accident can destroy all files in your computer forever.
- Clear the console:
  - CMD/PowerShell: `cls`
  - PowerShell/Bash: `clear` (yes, both work with PowerShell)
- Open the file explorer:
  - CMD/PowerShell: `start <folder_name>` - Tip: To open it in the current folder, use `start .`
  - PowerShell: `ii <folder_name>` - Tip: `ii .` works as well.
  - Bash: *It depends.* On MacOS, use `open <folder_name>`. On Linux, use `gnome-open <folder_name>`, `nautilus <folder_name>` or something relevant to your distribution.
- VS Code commands (works with all 3 languages):
    - Open the current folder in VS Code as a new project: `code .`
    - Open a file in VS Code and create it if it doesn't exist: `code <file_name>`

## What's the difference between Git and GitHub?

- Git is a software that allows you to track changes in your code, collaborate with others and do other cool stuff.
- GitHub is a website which allows you to host your Git repositories (that is your projects) online to share code and synchronise your work with others. It is not the only website hosting Git repositories, albeit the most popular one.

## Using Git and GitHub

### At the beginning

- Make sure you have Git installed first. For this, open your terminal and run the command `git`. If you do not get an error, it means Git is installed and correctly configured.
- If you're not comfortable with the terminal for now, you can install Github Desktop. It is mostly adapted for beginners with a simple and clear interface, but it cannot do everything you can do in a terminal, so you will have to use the commands at some point (and it's much more efficient to use the terminal, especially if you work on VS Code which has an integrated terminal). There are not so many commands and you don't have to know them by heart, so don't be scared.
- To get the project on your machine and synchronise it with others, you have to clone the repository I made (make sure you have approved my collaboration request first).
  - On GitHub Desktop: `File > Clone repository > Github.com > mi-1000/ftf`
  - CMD/PowerShell/Bash (make sure you're in the right folder before cloning) : `git clone https://github.com/mi-1000/ftf`
- One nice feature of Git is branches: imagine the project as a tree, every change you make being a leaf, and branches allowing you to split the work between different people and/or functionalities. Thus, if you make a change on one branch, it doesn't affect the other ones. You can then merge branches to one another to update functionalities step by step.
- The main branch in our project is called `main`, it is the one where we put all the code that is working and that we are sure we will not change anymore. For all the work in progress, we use other branches.
-  We do that by creating a "pull request", and asking for a code review to others. After corrections have been made if needed and once everybody agrees your code is working, we can merge your code into the `main` branch.
- **Never push changes to the `main` branch directly! Always create a pull request or work on a separate branch!**
- Always make sure you're working on the right branch:
  - On GitHub Desktop: `Current branch`
  - CMD/PowerShell/Bash: `git branch` - To switch branches: `git switch <branch>`
- Anytime you start working on the project or on another branch, you need to pull the latest changes done by others so that you stay up-to-date with the project:
  - On GitHub Desktop: `Fetch origin > Pull origin`
  - CMD/Powershell/Bash: `git pull`
- Same as when you work on MS Word for example, you need to save your work regularly. Git allows you to choose which files you want to track:
  - On GitHub Desktop: Everything by default, except what's in the `.gitignore` file.
  - CMD/PowerShell/Bash: `git add <your file(s)>` - To track everything in the project (redo this once you create a new file, running from the root of the project): `git add .` - Files in `.gitignore` are excluded.

### What is a `.gitignore`?

- It is a file that lists all the files or file patterns from your project that you don't want to upload to GitHub. This includes your Python virtual environment (I will come back to this later, for our project you will have to name it either `env`, `venv` or `.venv`), environment variables (you will have to name this file `.env`, I'll also come back to that later), binary files, files not relevant to the project, etc.
- To tell Git to ignore a file, just add a new line: `<file_name>`. File names are always considered relative to the root of the project.
- To tell Git to ignore a specific file pattern, you can use the wildcard character `*`:
  - `my_folder/my_subfolder/*` ignores all the content in `my_folder/my_subfolder`.
  - `*.py` ignores all the Python files.
  - `*/test/*.json` ignores all the JSON files in all the folders named `test`.
- You can add exceptions with the bang character `!`:
  - `!example.py` tells Git to track `example.py`, even if you added the line `*.py`.
- You can use hashtags `#` to add comments like in Python.
- (Do not touch this file if you are unsure what you are doing, and always make sure you do not upload sensitive data by mistake, because it will be tracked by Git and anybody will be able to find it even if it does not appear in the final version of the project, this is why it is best to ask everybody first)

### Let's come back to Git functionalities

- Git allows you to store your changes locally even if you don't have an Internet access:
  - On GitHub Desktop: `Commit to <branch>`
  - CMD/PowerShell/Bash: `git commit -a -m "<a_short_summary_of_your_changes>"` - The flag `-a` stands for "all", but you can commit some specific files only if you prefer, by specifying their name instead
- You then might want to share your changes with others and upload them to the remote repository on Github, so that others can pull your changes:
  - On GitHub Desktop: `Push changes`
  - CMD/PowerShell/Bash: `git push`
- That's about it for a start, you will not need to know more complex stuff for now 😃

## How to correctly set up your Python project

- Now you have set up Git and you know basic terminal commands, it is time to set up Python!
- First of all, you need to make sure you have `pip` correctly installed. In short, `pip` is a tool that will allow you to download Python packages/libraries directly from your terminal, instead of searching for them on the internet, and you will use it *a lot*. It should normally have been installed along with Python, but it never hurts to check:
  - CMD/PowerShell: `py -m ensurepip --upgrade` - Note: This does nothing if you already have the latest version of pip, updates it if you have an older version, and installs the last version if you didn't have it.
  - Bash: `python -m ensurepip --upgrade` - Note: If `python` is not working, try to use `python3` instead.
- The first thing you need to do whenever you start working on the project is to make sure your virtual environment is correctly set up. It will allow to separate your project files from the rest, especially when it comes to dependencies, and not pollute your computer with useless stuff, while making your project easier to maintain.
- You can name your virtual environment whichever name you want, but, in practice, common names are `venv` or `.venv`, so anybody instantly knows what it's about. I will use `.venv` in the next examples so make sure to change it if you choose another name, and add it to `.gitignore`.
- To create a virtual environment for your project, place yourself in the root folder, and run the following:
  - CMD/PowerShell: `py -m venv .venv`
  - Bash: `python -m venv .venv`
- You now need to activate your virtual environment:
  - CMD: `call .venv/Scripts/activate`
  - PowerShell: `.venv/Scripts/Activate.ps1` - Note: if you get an error message, try to run `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` first.
  - Bash: `source .venv/bin/activate` (if it doesn't work, use `. .venv/bin/activate` instead)
- You should now see lines in the terminal starting with `(.venv)` if you have correctly activated it.
- To deactivate it:
  - CMD/PowerShell/Bash: `deactivate`
- Always make sure your virtual environment is activated while you're working on the project.
- You can now safely install dependencies for the project without interfering with your system packages. It is very simple to install a package using `pip`:
  - CMD/PowerShell/Bash: `pip install <package_name>` - Example: To install `transformers`, run `pip install transformers` within the project root folder (with your virtual environment activated).
- A project typically needs several of such dependencies to work properly. As we do not push our virtual environment to GitHub, everybody needs to install the required packages on their own.
- To make sure everybody can easily install all the necessary packages without running `pip install <package_name>` tens of times, and to also ensure we all work with the same version of each dependency, we will use a special file named `requirements.txt`, that will list all the dependencies used in our project along with their corresponding version (if applicable). We then just have to run `pip install -r requirements.txt` regularly to keep our packages up-to-date, as `requirements.txt` will be a file shared by everyone.
- When a piece of code you add requires a new dependency, you need to add it to `requirements.txt`. But programmers are lazy, so run `pip freeze > requirements.txt` instead (with your virtual environment activated), or `py -m  pipreqs.pipreqs --encoding utf-8 .` (CMD/PowerShell)/`python -m  pipreqs.pipreqs --encoding utf-8 .` (Bash), which is a better practice, but you will have to install it using `pip install pipreqs` first.

### Environment variables

- Environment variables are not specific to Python, but we will use them in our project. They are a set of key-value pairs (i.e. `PASSWORD=1234`) that we will use frequently across the whole project.
- For this, we create a file called `.env`, where we store all sensitive data like passwords, API keys, database accesses etc., as well as stuff like e.g. the name of the model we are running.
- This file is personal and shall not be shared on GitHub. If we need to share data relative to environment variables, we should use Discord instead, or even face-to-face if possible. Yes, it's annoying, but it's a matter of security, and also a good habit to take for later.
- We can access environment variables from anywhere in our project using `dotenv.load_dotenv()` followed by `os.environ.get("<variable>")` (you have to install the relevant packages first).
- We can also add comments in the `.env` file the same way as in Python.
- We can store encrypted values for the most sensitive ones, and then decrypt them when reading them from the `.env` file.

- That's it 😀
