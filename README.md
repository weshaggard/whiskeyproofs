<link href="https://fonts.googleapis.com/css2?family=Cookie&display=swap" rel="stylesheet">

<a href="https://www.buymeacoffee.com/whiskeyproofs" style="display:inline-flex; align-items:center; gap:8px; padding:8px 16px; border:2px solid #b8956a; border-radius:8px; background-color:#b8956a; text-decoration:none; color:#ffffff; font-family:'Cookie',cursive; font-size:1.5rem; font-weight:400; transition:all 0.2s ease;">
  By me a drink <img src="assets/whiskeyglass.png" alt="Whiskey glass" height="28" style="display:inline-block;">
</a>

# Whiskey Proofs Index

A Jekyll-based static website for storing and displaying whiskey information. This site serves as a reference guide for finding specific details about whiskey batches, release years, and proof values.

## 🥃 Use Cases

This site helps answer questions like:
- "What year was George T. Stagg released that had a proof of 135.4?"
- "What was the proof of Elijah Craig C923?"
- "Which batches of Stagg Jr were released in 2023?"

## 🔍 Features

- **Interactive Table**: Browse whiskey data in a clean, sortable table
- **Search & Filter**: Find whiskies by name, distillery, or type
- **Responsive Design**: Works great on desktop and mobile devices
- **Easy Updates**: Add new whiskies by simply editing a CSV file

## 📊 Adding/Editing Whiskey Entries

All whiskey data is stored in `_data/whiskeyindex.csv`. To add or edit entries:

1. Open `_data/whiskeyindex.csv` in any text editor or spreadsheet application
2. Each row represents one whiskey with the following columns:
   - **Name**: The name of the whiskey
   - **Distillery**: The distillery that produced it
   - **Batch**: Batch number or identifier (e.g., "Fall 2023", "C923", "Batch 22")
   - **Age**: Age statement in years (use "Unknown" if not specified)
   - **Proof**: Alcohol proof (numeric value)
   - **Type**: Type of whiskey (Bourbon, Scotch, Rye, Irish, etc.)
   - **ReleaseYear**: Year of release

### Example Entry
```csv
George T. Stagg,Buffalo Trace Antique Collection,Fall 2023,15,135.4,Bourbon,2023
Elijah Craig Barrel Proof,Heaven Hill,C923,12,135.8,Bourbon,2023
```

### Tips for Editing
- Keep the header row intact
- Use commas to separate values
- If a value contains a comma, wrap it in quotes: `"Distiller's Select, Premium"`
- Save the file with UTF-8 encoding

## 🚀 Running Locally

To run the site on your local machine for development:

### Prerequisites
- Ruby (version 2.7 or higher)
- Bundler gem

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/weshaggard/whiskeydata.git
   cd whiskeydata
   ```

2. **Install dependencies**
   ```bash
   bundle install
   ```

3. **Run the Jekyll server**
   ```bash
   bundle exec jekyll serve
   ```

4. **View the site**
   - Open your browser and navigate to `http://localhost:4000`
   - The site will automatically reload when you make changes to files

### Common Commands

- **Build the site**: `bundle exec jekyll build`
- **Serve with drafts**: `bundle exec jekyll serve --drafts`
- **Serve on a different port**: `bundle exec jekyll serve --port 4001`

## 🌐 GitHub Pages Deployment

This site is designed to work seamlessly with GitHub Pages.

### Setup Steps

1. **Enable GitHub Pages**
   - Go to your repository settings on GitHub
   - Navigate to the "Pages" section
   - Under "Source", select the branch you want to deploy (typically `main`)
   - Click "Save"

2. **Wait for deployment**
   - GitHub Pages will automatically build and deploy your site
   - This usually takes 1-2 minutes
   - Your site will be available at `https://[username].github.io/[repository-name]/`

3. **Update site URL** (Optional)
   - Edit `_config.yml` and update the `url` and `baseurl` fields:
     ```yaml
     url: "https://weshaggard.github.io"
     baseurl: "/whiskeydata"
     ```

### Automatic Updates

Once GitHub Pages is enabled:
- Any changes pushed to the main branch will automatically trigger a rebuild
- Updates to `_data/whiskeyindex.csv` will be reflected on the live site within minutes
- No manual deployment needed!

## 📁 Project Structure

```
whiskeyproofs/
├── _config.yml          # Jekyll configuration
├── _data/
│   └── whiskeyindex.csv     # Whiskey data (edit this file to add/update entries)
├── index.html           # Main page with whiskey table
├── Gemfile              # Ruby dependencies
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## 🎨 Customization

### Changing the Theme
The site uses the `minima` theme by default. To change it:
1. Edit `_config.yml`
2. Change the `theme` value to another [supported GitHub Pages theme](https://pages.github.com/themes/)

### Modifying Styles
CSS styles are embedded in `index.html`. Look for the `<style>` section to customize:
- Colors
- Table appearance
- Layout and spacing

### Adding More Data Fields
To add additional columns to the whiskey data:
1. Add the new column to `_data/whiskeyindex.csv`
2. Update `index.html` to display the new field in the table

## 🛠️ Troubleshooting

**Site not updating?**
- Clear your browser cache
- Wait a few minutes for GitHub Pages to rebuild
- Check the Actions tab in your GitHub repository for build status

**Local server not working?**
- Make sure Ruby and Bundler are installed: `ruby -v` and `bundle -v`
- Try removing `Gemfile.lock` and running `bundle install` again
- Check for error messages in the terminal

**CSV data not showing?**
- Verify the CSV file is saved with UTF-8 encoding
- Check that the header row matches exactly: `Name,Distillery,Batch,Age,Proof,Type,ReleaseYear`
- Ensure there are no syntax errors in the CSV file

## 📝 License

This project is open source and available for use and modification.

## 🤝 Contributing

Feel free to submit issues or pull requests to improve the site!
