# Web crawler weibo

 The toolbox to collect posts from https://weibo.com

![](https://shields.io/badge/dependencies-Python_3.12-blue)
![](https://shields.io/badge/OS-Windows_10_64--bit-navy)

## Install

If it's the first time to use this program, please create a Python virtual environment and run

```
pip install -r requirements.txt
```

In the minimum example, I assume the computer has installed Google Chrome in the default path. If Google Chrome is installed, but in the customized path, please run the following command and set `chrome_user_data` manually.

If you have Google Chrome version 130 or above, install [J2TEAM cookies](https://chromewebstore.google.com/detail/j2team-cookies/okpidcojinmlaakglciglbpcpajaibco) extension. Otherwise, read the note below.

> [!NOTE]
>
> If you don't have Google Chrome, but your browser is also chromium-based (like Microsoft Edge) and support `*.crx` extensions, you have two options.
>
> **Option 1.**  Get the extracted `*.crx` package of J2TEAM cookies and install.
>
> **Option 2.**  Copy the cookies from developer console:
>
> 1. Press F12 to open the developer console.
> 2. Go to "Application" tab, then "Storage > Cookies > URL" tab in the left sidebar, where URL is the website mentioned in "getting the cookies file" part.
> 3. Drag the mouse to select the whole table and copy.
> 4. Paste the data in Microsoft Excel or Notepad software. Clean the data to the same table as you see from developer console GUI.
> 5. Save the cookies file to `raw/cookies.csv` (the target path is mentioned in `auth.py` script, and may vary if the program is updated. *You need to save directly because the format is different from exported by J2TEAM cookies.*
>
> If your browser also have a extension web store (like Mozilla Firefox), you can use J2TEAM cookies or alternatives which can produce the same format.



## Usage

**Get cookies**

Run `python auth.py` to read the cookies file:

1. Visit https://weibo.com/explore and export the cookies by J2TEAM cookies.
2. Select this cookies file when the program requires.

(Optional) You can copy this program, including generated files, to a non-graphic Linux machine and retrieve posts before the cookies expire.

**Collect posts**

For example, to search posts containing "GitHub" at 11:00-12:00 (UTC+8) on August 15, 2023. Retrieve at most 2 pages (10 posts per page).

```
python search.py --query="GitHub" --start_time=2023-08-15-11 --end_time=2023-08-15-12 --max_page=2
```

For more search options, run the following command.

```
python search.py --help
```

If the database path is by default, the results are saved in `posts.db` database.

Possible reasons for empty results:

1. Searching non-Chinese strings will usually return nothing, because "Weibo" is a Chinese social media. 
2. There are several hours' delay before posts appear in the search engine. It's better to search posts 2 days ago.

**Database schema**

View the `search` table and get the table name. The data structure is shown as follows.

| Name       | Type | Description                                                  |
| ---------- | ---- | ------------------------------------------------------------ |
| query      | text | The searching words.                                         |
| start_time | text | Posts from this hour will be collected. The [format code](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes) is %Y-%m-%d-%H |
| end_time   | text | Posts till this hour will be collected. The format is the same as `start_time` |
| table      | text | The table name that this query's results are stored.         |

According to this table name, view the results in the mentioned table.


The data structure of the search results:

| Name        | Type | Description                                                  |
| ----------- | ---- | ------------------------------------------------------------ |
| avatar      | text | Link to the avatar of the post author.                       |
| nickname    | text | Username of the post author.                                 |
| user_id     | text | User ID of the post author.                                  |
| posted_time | text | The time when the post was published. Its format can be either seconds/hours/days ago (in Chinese) or an exact datetime with or without years. |
| source      | text | How the post author visits "weibo". It can be either the device name or the topic (tag) name. |
| weibo_id    | text |                                                              |
| content     | text | The main body of the post. This column of fast reposts will be empty. |
| reposts     | text | Number of reposts. Chinese character "万" may appear in this field, as well as `comments` and `likes`, which means "multiply 10,000". |
| comments    | text | Number of comments.                                          |
| likes       | text | Number of likes.                                             |

SQL statements:

<table>
<thead>
<tr><th>Name</th><th>Table</th><th>Description</th></tr>
</thead>
<tbody>
    <tr>
        <td>User profile URL</td>
        <td>search results</td>
        <td><code>'https://weibo.com/u/' || user_id</code></td>
    </tr>
    <tr>
        <td>Post URL</td>
        <td>search results</td>
        <td><code>'https://weibo.com/' || user_id || '/' || weibo_id</code></td>
    </tr>
</tbody>
</table>
