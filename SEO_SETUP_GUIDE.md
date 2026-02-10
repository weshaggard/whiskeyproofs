# SEO Setup and Submission Guide

This guide will help you complete the SEO setup for whiskeyproofs.com and submit your site to search engines.

## 1. Google Search Console Setup

Google Search Console helps you monitor how Google indexes your site and appears in search results.

### Steps:

1. **Go to Google Search Console**: https://search.google.com/search-console
2. **Add Property**: Click "Add Property" and enter `https://whiskeyproofs.com`
3. **Verify Ownership**: Choose "HTML tag" verification method
4. **Get Verification Code**: Copy the code from the meta tag (the part that looks like `content="abc123xyz..."`)
5. **Update Site**: 
   - Open `_includes/head-custom.html`
   - Replace `GOOGLE_VERIFICATION_CODE_PLACEHOLDER` with your actual verification code
   - Commit and push changes
   - Wait for GitHub Pages to rebuild (1-2 minutes)
6. **Complete Verification**: Click "Verify" in Google Search Console
7. **Submit Sitemap**: In Search Console, go to "Sitemaps" and submit: `https://whiskeyproofs.com/sitemap.xml`

### What to Monitor:

- **Coverage**: Check which pages are indexed
- **Performance**: See search queries, clicks, and impressions
- **Enhancements**: Monitor structured data (schema.org markup)
- **Core Web Vitals**: Track page speed and user experience

## 2. Bing Webmaster Tools Setup

Bing Webmaster Tools is similar to Google Search Console but for Bing/Microsoft search.

### Steps:

1. **Go to Bing Webmaster Tools**: https://www.bing.com/webmasters
2. **Add Site**: Enter `https://whiskeyproofs.com`
3. **Verify Ownership**: Choose "HTML Meta Tag" option
4. **Get Verification Code**: Copy the code (looks like `content="123ABC..."`)
5. **Update Site**:
   - Open `_includes/head-custom.html`
   - Replace `BING_VERIFICATION_CODE_PLACEHOLDER` with your actual verification code
   - Commit and push changes
   - Wait for rebuild
6. **Complete Verification**: Click verify in Bing Webmaster Tools
7. **Submit Sitemap**: Submit `https://whiskeyproofs.com/sitemap.xml`

## 3. Submit to Search Engines Directly

While sitemaps help, you can also submit URLs directly:

### Google:
- **URL Inspection Tool**: In Search Console, use the URL inspection tool to request indexing for specific pages
- **Submit URL**: https://search.google.com/search-console

### Bing:
- **URL Submission**: Use the URL submission API or manual submission in Webmaster Tools
- **IndexNow**: Bing supports IndexNow for faster indexing (can be automated)

## 4. Improve Search Visibility

### Content Optimization:

✅ **Already Implemented**:
- Comprehensive meta tags (title, description, keywords)
- Schema.org structured data (WebSite, Dataset, FAQ)
- Sitemap.xml for search engine crawling
- robots.txt allowing all crawlers
- Internal linking between pages
- FAQ page with FAQ schema
- About page with detailed information
- Canonical URLs
- Open Graph and Twitter Card meta tags

### Recommended Actions:

1. **Create Quality Content**:
   - Add blog posts about whiskey releases
   - Create guides (e.g., "Understanding Barrel Proof Whiskey")
   - Add reviews or tasting notes (if appropriate)

2. **Build Backlinks**:
   - Share on whiskey forums and communities
   - Reach out to whiskey bloggers and reviewers
   - Submit to whiskey directories
   - Engage with whiskey communities on Reddit

3. **Social Media**:
   - Share updates on Twitter/X
   - Post in whiskey Facebook groups
   - Use relevant hashtags (#bourbon #whiskey #barrelproof)
   - Engage with whiskey influencers

4. **Regular Updates**:
   - Add new releases promptly
   - Update TTB labels as they're approved
   - Keep data accurate and current

## 5. Monitor and Iterate

### Tools to Use:

- **Google Search Console**: Track indexing and search performance
- **Google Analytics**: Already configured on site (GA4: G-938KTTLKL3)
- **Bing Webmaster Tools**: Monitor Bing search performance
- **Schema Markup Validator**: https://validator.schema.org/

### Key Metrics to Watch:

- Number of indexed pages
- Search impressions and clicks
- Average position in search results
- Click-through rate (CTR)
- Core Web Vitals scores
- Mobile usability

## 6. Advanced SEO Opportunities

### Future Enhancements:

1. **Individual Product Pages**:
   - Create dedicated pages for popular whiskeys
   - Add detailed information, reviews, comparisons
   - Use Product schema markup

2. **Blog/News Section**:
   - Announce new releases
   - Write about industry news
   - Create educational content

3. **Enhanced Structured Data**:
   - Add BreadcrumbList schema
   - Use Organization schema with more details
   - Add Review/Rating schema if you collect ratings

4. **Performance Optimization**:
   - Optimize images (already using PNG, consider WebP)
   - Minimize JavaScript and CSS
   - Leverage browser caching
   - Use CDN for assets

5. **Local SEO** (if applicable):
   - Add LocalBusiness schema
   - Create Google Business Profile
   - Get listed in local directories

## 7. Search Query Targeting

Your site should now rank well for queries like:

- "bourbon proof index"
- "George T Stagg proof by year"
- "Elijah Craig barrel proof batches"
- "whiskey batch numbers"
- "bourbon release years"
- "barrel proof whiskey database"
- "BTAC proof values"
- "[specific bourbon] proof"

## 8. Checklist

- [ ] Get Google Search Console verification code
- [ ] Update `_includes/head-custom.html` with Google code
- [ ] Get Bing Webmaster Tools verification code
- [ ] Update `_includes/head-custom.html` with Bing code
- [ ] Commit and push changes
- [ ] Wait for site rebuild
- [ ] Verify ownership in Google Search Console
- [ ] Verify ownership in Bing Webmaster Tools
- [ ] Submit sitemap to Google
- [ ] Submit sitemap to Bing
- [ ] Request indexing for main pages
- [ ] Monitor Search Console for issues
- [ ] Share site on social media
- [ ] Reach out to whiskey communities
- [ ] Regular content updates

## Need Help?

If you have questions or need assistance:
- Check Google Search Console Help: https://support.google.com/webmasters
- Check Bing Webmaster Help: https://www.bing.com/webmasters/help
- Search engine optimization basics: https://developers.google.com/search/docs/fundamentals/seo-starter-guide

---

**Note**: SEO is a gradual process. It may take several weeks for search engines to fully index and rank your site. Keep content fresh and quality high for best results.
