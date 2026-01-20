# Plugin to copy CSV files from _data to assets/data during build
# This ensures the dataset is publicly accessible without duplicating it in the repo

Jekyll::Hooks.register :site, :post_write do |site|
  # Source and destination paths
  source_file = File.join(site.source, '_data', 'whiskeyindex.csv')
  dest_dir = File.join(site.dest, 'assets', 'data')
  dest_file = File.join(dest_dir, 'whiskeyindex.csv')
  
  # Create destination directory if it doesn't exist
  FileUtils.mkdir_p(dest_dir)
  
  # Copy the CSV file
  if File.exist?(source_file)
    FileUtils.cp(source_file, dest_file)
    puts "Copied whiskeyindex.csv to assets/data/"
  else
    puts "Warning: whiskeyindex.csv not found in _data/"
  end
end
