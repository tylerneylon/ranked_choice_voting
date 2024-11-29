# ranked_choice_voting

*A Python script to find ranked-choice voting winners based on a google form.*

Specifically, this script implements
[instant runoff voting](https://en.wikipedia.org/wiki/Instant-runoff_voting)
based on data (in an expected format) from Google Forms.

I made this script to help a book club that I joined to analyze ranked-choice
votes about which book to read next. Hence sometimes the script itself refers to
things being voted on as "books," but the algorithm is general and can work no
matter what you're voting on.

## Usage

```
        ./ranked_choice_votes.py <google_form_data.csv>

    This interactive script determines the winner of a ranked-choice
    vote based on data from a Google form. Please provide the name of google
    form's csv file to get started.
```

**How to download the CSV file from Google Forms**

* From your Google Form, click on *responses*.
* Click on the three-dot icon near the upper-right.
  (Next to "Link to Sheets.")
* Click on *Download responses (.csv)*

## Question / CSV Data Format

This voting script assumes that:
 * We're working with a CSV file from Google forms.
 * That the questions all begin with the title of the books.
   Specifically, I'll use the first line of each question as a title.
 * That the ranked choice votes are of the form "First choice"
   up through a maximum of "Fifth choice". Case doesn't matter.
