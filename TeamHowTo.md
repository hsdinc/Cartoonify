## TEAM HOW TO -- GIT BUG TRACKING 

### Pull requests
When pushing new features to the Cartoonify Github Repo, all contributors must participate in a code review. 
All members of the Cartoonify team must review each pull request so that every one can be on the same page 
at all times. Pull requests are set to require at least **4 code reviews**, which ensures that every member of the 
initial 5 Cartoonify members will have seen the changes.

### Bug Reports:

When reporting a bug, all team members should use git bug tracking. We will be using the following repo https://github.com/MichaelMure/git-bug to organize our bug tracking. Here is a quick guide to get this set up on your machine.

1. Get the language Go. 

If you do not have a mac, follow these instructions: https://golang.org/doc/install

If you are on a Mac: Run the following commands in the directory of Cartoonify!  
`export GOPATH="${HOME}/.go"`  
`export GOROOT="$(brew --prefix golang)/libexec"`
`export PATH="$PATH:${GOPATH}/bin:${GOROOT}/bin"`
`test -d "${GOPATH}" || mkdir "${GOPATH}"`
`test -d "${GOPATH}/src/github.com" || mkdir -p "${GOPATH}/src/github.com"`

Now make sure that you have [homebrew](https://brew.sh/) installed and then install go!

`brew install go`  

2. Now we can use bug tracking!:  

Run this line in your terminal: `export PATH=$PATH:$(go env GOROOT)/bin:$(go env GOPATH)/bin`

3. Create a new user:  
`git bug user create`

4. Use the following syntax to add a bug:
`git-bug add -t --title [YOUR TITLE HERE] bug -m --message [YOUR MESSAGE HERE].`

5. Push your bug:  
`git bug push`   
and pull new bugs  
`git bug pull`

6. Extra fun syntax:  
`git bug ls` list bugs
`git bug termui` fun UI to use!



### Resources:
https://ahmadawais.com/install-go-lang-on-macos-with-homebrew/
https://github.com/MichaelMure/git-bug
