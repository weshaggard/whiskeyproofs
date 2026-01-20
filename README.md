[![Buy me a drink](assets/buymeadrink.png "Buy me a drink")](https://www.buymeacoffee.com/whiskeyproofs)

# Whiskey proof index

A Jekyll-based static website for storing and displaying whiskey information. This site serves as a reference guide for finding specific details about whiskey batches, release years, and proof values.

## 🥃 Use Cases

This site helps answer questions like:
- "What year was George T. Stagg released that had a proof of 135.4?"
- "What was the proof of Elijah Craig C923?"
- "Which batches of Stagg Jr were released in 2023?"

## 🔍 Features

- **Interactive Table**: Browse whiskey data in a clean, sortable table
- **Search & Filter**: Find whiskies by name, distillery, or type
- **TTB COLA Links**: Direct links to official TTB approval documents when available (hidden by default, show with `?showTTB=true`)
- **Responsive Design**: Works great on desktop and mobile devices
- **Easy Updates**: Add new whiskies by simply editing a CSV file

## 📊 Adding/Editing Whiskey Entries

All whiskey data is stored in `_data/whiskeyindex.csv`. To add or edit entries:

1. Open `_data/whiskeyindex.csv` in any text editor or spreadsheet application
2. Each row represents one whiskey with the following columns:
   - **Name**: The name of the whiskey
   - **Batch**: Batch number or identifier (e.g., "Fall 2023", "C923", "Batch 22")
   - **Age**: Age statement in years (leave empty if not specified)
   - **Proof**: Alcohol proof (numeric value)
   - **ReleaseYear**: Year of release
   - **Distillery**: The distillery that produced it
   - **Type**: Type of whiskey (Bourbon, Scotch, Rye, Irish, etc.)
   - **TTB_ID**: (Optional) TTB COLA approval ID for creating a clickable link to the official approval
   - **url**: (Optional) External URL for the whiskey product page. When provided, the batch text becomes a clickable link

### Example Entry
```csv
Angel's Envy Cask Strength,2025,10,122.6,2025,Angel's Envy,Bourbon,22089001000941,
Birthday Bourbon,2023,12,96.0,2023,Old Forester,Bourbon,,https://www.oldforester.com/products/2023-birthday-bourbon/
```

### Product Links
When a URL is provided, the batch text in the table becomes a clickable link to the product's official page. This is particularly useful for limited releases or special editions that have dedicated product pages.

### TTB COLA Links
When a TTB_ID is provided, a clickable link (🔗) will appear in the table that opens the official TTB COLA approval page. The TTB column is hidden by default - add `?showTTB=true` to the URL to display it. To find TTB IDs:
1. Visit [TTB COLA Public Registry](https://ttbonline.gov/colasonline/publicSearchColasBasic.do)
2. Search for the whiskey brand and batch
3. Copy the TTB ID from the URL (e.g., `22089001000941` from `https://ttbonline.gov/colasonline/viewColaDetails.do?action=publicFormDisplay&ttbid=22089001000941`)
4. Add it to the TTB_ID column in the CSV

### Data Sorting Rules

The CSV file maintains a specific sort order:
1. **Primary Sort**: Product Name (ascending/alphabetical)
2. **Secondary Sort**: Batch (descending - newest/latest first within each product)

**Important**: For batches with numbers (like "Batch 15", "Batch 2"), they are sorted **numerically** (15 before 2), not alphabetically.

### Tips for Editing
- Keep the header row intact
- Use commas to separate values
- If a value contains a comma, wrap it in quotes: `"Distiller's Select, Premium"`
- Leave the TTB_ID column empty if not available
- Save the file with UTF-8 encoding
- After editing, run the validation script to ensure data quality and sorting

### Validating Your Changes

A validation script is included to check data quality and sort order:

```bash
python3 .github/scripts/validate_whiskey_data.py
```

This script will:
- Verify all required fields are present
- Check for valid proof values and release years
- Detect duplicate entries
- Ensure proper sort order (Name ascending, Batch descending with numeric sorting)

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
│   └── whiskeyindex.csv # Whiskey data (edit this file to add/update entries)
├── .github/
│   └── workflows/
│       └── jekyll.yml   # Copies CSV to /data/ during deployment
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
