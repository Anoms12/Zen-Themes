# Zen-Themes
A curation of themes for Zen browser using userChrome loader


# Zen Themer GUI
Run the following scripts in your terminal to be able to accses the user friendly themer

```bash
# Clone the repository
git clone https://github.com/Anoms12/Zen-Themes.git
cd Zen-Themes

# Run the script
python zen-themer.py
```

## How does the Zen Themer work?
The themer checks to see if you have Zen installed and have setup a `userChrome.css` folder, prompts you to chose the profile you would like to add the zen theme into, then creates a new folder adding the selected `CSS` from the GitHub repo and adding the correct `@import` statement into the `userChrome.css`

## Why am I getting an error locating profiles
add your `profiles.ini` to the profiles folder in Zen then it should work. This is a tmp solution, make sure to duplicate the folder and not move it.

## How Does Zen Themer Work?

**Zen Themer works by automating the process of applying themes to Zen browser. Here’s how it works:**

   1. Zen Installation Check: The script verifies if Zen is installed and checks for the presence of a userChrome.css folder.
   1. Profile Selection: You will be prompted to select which profile you want to apply the Zen theme to.
   1. Theme Setup: After selecting the theme, the script creates a new folder, downloads the selected CSS from the GitHub repository, and updates the userChrome.css file with the necessary @import statements.

**Features**

  * User-Friendly Interface: The Zen Themer provides a simple way to browse, select, and apply themes without manually editing files.
   * Automatic Setup: The tool handles everything, from downloading the CSS files to appending the correct imports into userChrome.css.
   * Cross-Platform: Tested on Windows 11 but should work on macOS and Linux as well.

**Contributing**

Feel free to fork this repository, open issues, or contribute new themes via Pull requests!
