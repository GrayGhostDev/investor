# GitHub Repository Setup Guide

Follow these steps to create a GitHub repository for your Investor Search Platform:

## 1. Create a new repository on GitHub

1. Go to [GitHub](https://github.com/) and sign in to your account.
2. Click on the "+" icon in the top-right corner and select "New repository".
3. Enter "investor-search-platform" as the repository name.
4. Add a description: "A comprehensive web application for startups to find, analyze, and connect with potential investors."
5. Choose "Public" or "Private" visibility based on your preference.
6. Do NOT initialize the repository with a README, .gitignore, or license (we've already created these locally).
7. Click "Create repository".

## 2. Connect your local repository to GitHub

After creating the repository on GitHub, you'll see instructions for pushing an existing repository. Run the following commands in your terminal:

```bash
# Add the GitHub repository as a remote
git remote add origin https://github.com/YOUR_USERNAME/investor-search-platform.git

# Push your local repository to GitHub
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

## 3. Verify the repository

1. Refresh the GitHub page to see your code.
2. Ensure all files are properly uploaded and the README is displayed correctly.

## 4. Set up branch protection (optional)

For collaborative projects, you might want to set up branch protection:

1. Go to the repository settings.
2. Click on "Branches" in the left sidebar.
3. Under "Branch protection rules", click "Add rule".
4. Enter "main" as the branch name pattern.
5. Select appropriate protection options (e.g., require pull request reviews).
6. Click "Create" to save the rule.

## 5. Enable GitHub Pages (optional)

If you want to create a project website:

1. Go to the repository settings.
2. Scroll down to "GitHub Pages".
3. Select the branch to use for GitHub Pages (usually "main").
4. Choose the "/docs" folder or the root folder.
5. Click "Save".

Your project website will be available at `https://YOUR_USERNAME.github.io/investor-search-platform/`.
