#!/usr/bin/env python3

import os
import wget
import argparse
from subprocess import check_output
from colorama import Fore, Back, Style
from git import Repo



#unfortunately, the command git cat-file and git ls-tree don't seem implemented in gitpython, todo: someday creaye PR to add support natively
#in the meantime, opening a subprocess works fine as long as git is installed
def git_ls_tree(sha1):
    os.chdir('./rebuilt_repo')
    res = check_output(['git', 'ls-tree', sha1]).decode('utf-8')
    os.chdir('..')
    return res

def git_cat_file(sha1, arg):
    os.chdir('./rebuilt_repo')
    res = check_output(['git', 'cat-file', arg, sha1]).decode('utf-8').strip()
    os.chdir('..')
    return res

def get_indexed_object_type(sha1):
    git_object_type = git_cat_file(sha1, "-t")
    return git_object_type

def get_git_object(sha1):

    # if the hash for a commit is "c4cf8d23b703212c0fd92bf19f8cd55d7e4f27bd", it will be stored in .git/objects/c4/cf8d23b703212c0fd92bf19f8cd55d7e4f27bd
    git_object_name = sha1[2:]
    git_object_index = sha1[:2]
    full_url = EXPOSED_URL + "/" + git_object_index + "/" + git_object_name

    print("trying to download " + full_url)
    wget.download(full_url, git_object_name)

    if os.path.exists("./" + git_object_name):
        
        if not os.path.exists("./rebuilt_repo/objects/" + git_object_index):
            os.mkdir("./rebuilt_repo/objects/" + git_object_index)
        
        os.rename("./" + git_object_name, "./rebuilt_repo/objects/" + git_object_index + "/" +  git_object_name)
        print("\nthe file was downloaded successfully and indexed into the rebuilt_repo") 
    

def recursive_step(sha1, filename):
    get_git_object(sha1)

    git_object_type = get_indexed_object_type(sha1)

    if git_object_type == 'commit':

        #A commit object looks like the following :

        #tree <sha1>
        #parent <sha1>
        #author <sha1>
        #...

        res =  git_cat_file(sha1, "commit")
        next_object_hash = res.partition('\n')[0].partition(' ')[2]
        next_object_type = res.partition('\n')[0].partition(' ')[0]
        print("This commit points to the " + next_object_type + ' '  + next_object_hash) 
        

        print("\n---------------------------------------------------------------------------------------------------\n")

        if FOLLOW_PARENT_COMMIT:
            recursive_step(next_object_hash, filename)


    elif git_object_type == 'tree':

        if not os.path.exists(filename):
            os.mkdir(filename)
            print("directory " + filename + " has been built")

        print('\nthis tree contains :')
        tree_content = git_ls_tree(sha1)
        print(tree_content)
        

        for line in tree_content.splitlines():
            next_object_type = line.split(' ')[1]
            next_object_hash = line.split(' ')[2].split("\t")[0]
            next_object_name = line.split("\t")[1]

            print("\n---------------------------------------------------------------------------------------------------\n")
            
            recursive_step(next_object_hash, filename + '/' + next_object_name)

    elif git_object_type == 'blob':
        
        blob_content = git_cat_file(sha1, 'blob')
        text_file = open(filename, "w")
        text_file.write(blob_content)
        
        print(Back.GREEN + "The file " + filename + " has been retrieved")
        print(Style.RESET_ALL)

    else:
        print(Fore.RED + "error, unknown git object type")
        print(Style.RESET_ALL)


parser = argparse.ArgumentParser("python exposed_git_rebuilder")
parser.add_argument("exposed_url", help="url of the exposed repository", type=str)
parser.add_argument("last_commit_hash", help="sha1 of the last commit, can usually be found in . git/refs/heads/", type=str)
args = parser.parse_args()
print(args.exposed_url)

EXPOSED_URL = args.exposed_url + '/objects'
last_commit_hash = args.last_commit_hash

#Creating a git repo to host our retrieved files:
bare_repo = Repo.init(os.path.join(".", 'rebuilt_repo'), bare=True)
assert bare_repo.bare

FOLLOW_PARENT_COMMIT = True    #TODO: add a depth argument, a simple way to do it would be to count the '/' in the path then set this variable to false when depth is reached

print("starting the reconstruction from the first known hash " + last_commit_hash + "\n")
recursive_step(last_commit_hash, '.')
