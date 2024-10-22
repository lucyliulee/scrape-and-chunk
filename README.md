# Scraping Philosophy

The Notion help pages typically structured the help content with a header and paragraph details. In order to keep the right information together, I opted to record sections of each help article where the paragraph content is linked to the header. Since the scope of this scraping assignment was to scrape all the help articles excluding the guides in Notion Academy, those links were explicitly ignored. `char_length` was originally added in the parsing to help with chunking later. However, since I later added formatting in the chunks to maintain the context of `HEADER` and `CONTENT`, the length was no longer needed.

# Chunking Philosophy

The goal is to keep headers and paragraph content in the same chunk whenever possible. If the chunk were to be greater than the `max_chunk_size`, then a new chunk with the same header will be created. Content will always be split between chunks after the end of the paragraph content rather than in the middle of a sentence.

# Validation

I ran some simple validation to check the size of the chunks and contents. Some chunks were greater than the suggested 750 due to paragraph sections that were added to complete the related content together. Here are the results:

```
Total chunks: 1995
Valid lengths: 1990/1995 (99.75%)
Valid headers: 1995/1995 (100.00%)
Valid contents: 1995/1995 (100.00%)

Length distribution:
0-99 chars: 23 chunks
100-199 chars: 309 chunks
200-299 chars: 362 chunks
300-399 chars: 222 chunks
400-499 chars: 232 chunks
500-599 chars: 258 chunks
600-699 chars: 325 chunks
700-799 chars: 261 chunks
800-899 chars: 1 chunks
1000-1099 chars: 1 chunks
1200-1299 chars: 1 chunks

Detailed analysis:
Found 5 invalid chunks at indices: [654, 1552, 1554, 1753, 1988]
```

Example of invalid chunk:

```
HEADER: Customize your bar or line chart

CONTENT: Cumulative: You’ll see this option if your chart is showing Count or Sum and your X axis property is sorted in ascending order. Toggle on Cumulative if you want your chart to reflect the total amount of information gathered over time. Toggle off Cumulative if you want the chart to reflect the data for the current moment in time. For example, let’s say you have a chart where you’re tracking how many tasks you have completed. You completed two tasks yesterday, and three tasks today. If Cumulative is toggled on, you’ll see two tasks completed yesterday, and five tasks (two from yesterday, three from today) completed today. If Cumulative is toggled off, you’ll see two tasks completed yesterday, and three tasks completed today.
```
