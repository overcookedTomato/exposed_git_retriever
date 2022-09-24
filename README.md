# exposed_git_retriever
A pentest tool to retrieve all commits, trees and blobs from a .git repo exposed on a webserver. All these objects are then "indexed" in a local repo.

Basically a way less advanced alternative to https://github.com/internetwache/GitTools (at the time I initially wrote it for a pentest there was no tool that attempted to rebuild an entire repo, instead they all blindly downloaded as many blobs as possible). 
It was a fun project to code in a quick and dirty way but I will not support additional features or bug fix.
