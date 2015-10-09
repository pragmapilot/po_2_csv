# po_2_csv

Python conversion utility for translations.

This set of tools is designed to help developers and translators to preform translation of a web application. It extracts all the translatable resources to a translation matrix (in the form of a CSV) and is able to reapply the translation matrix back to the resource files.

Usage
=====

To extract all the strings from the `.po` files do the following:

`python3 po2csv.py <base_path> <output_file>`

Where:

`<base_path>`: the top-level folder from where the translatable resources can be found

`<output_file>`: the name of the CSV that will contain the translation matrix

Example: 

`python3 po2csv.py ./app translations.csv`

Now `translations.csv` holds a translation matrix like the following:

| msgid         | fuzzy? | en-en | de-de    | fr-fr    |
| ------------- |--------|-------|----------|----------|
| hello         |        |Hello! |          |          |
| bye           |        |Bye!   |          |          |

File can be opened with any spread sheet that supports CSV files. The translation matrix can be filled appropriately as the example below:

| msgid         | fuzzy? | en-en | de-de    | fr-fr    |
| ------------- |--------|-------|----------|----------|
| hello         |        |Hello! |Hallo!    |Bonjour!  |
| bye           |        |Bye!   |Lebewohl! |Au revoir!|

Now it's just a matter of reverting the process:

`python3 csv2po.py <base_path> <input_file>`

Where:

`<base_path>`: the top-level folder from where the translatable resources can be found

`<input_file>`: the name of the CSV that contains the translation matrix to apply to the resource files.

Example:

`python3 csv2po.py ./app translations.csv`

Now it's done! You can check the `.po` files to make sure the translated strings are there.

Goals
=====

1. Work within the context of Django Python's applications (easy to edit and change to match another folder structure).
2. Crawl the applications and gather all the translatable entries in a single CSV file preserving message ID and locale information. 
3. Remove any duplicated messages. 
4. Include any strings marked as fuzzy.
5. Work both ways: from `.po` to `.csv` and from `.csv` to `.po`.
6. Preserve '\n' characters.

Requirements
============

The tools were written to work with **Python3** but can be ported to Python2. This option was made as Python3 is more friendly regarding Unicode and encodings.

You must have [polib](http://polib.readthedocs.org/en/latest/installation.html#installing-polib) installed for Python3. Remember that you should use `pip3` to install polib for Python3.

Caveats
=======

The scripts are designed to work with Django localization folder structure:

`/app/locale/<locale-id>/LC_MESSAGES/<file>.po`

And:

`/app/locale/<locale-id>/LC_MESSAGES/<file>js.po`

If you your needs are slightly different you can easily tune it. *Hint*: check the `parse_locale` function.

Tests
====

A convenience test folder structure is provided so you can understand how it works before messing with your own project. It's obviously the `test` folder in the project. It emulates a scenario where three Django apps are present, each one with three locales. On the leaf folders you can find `django.po` and `djangojs.po` files with three translatable entries each The folder structure is the following:

>     test
>     |----po2csv
>           |-----app1
>           |     |-----locale
>           |           |----en-en  
>           |           |    |------django.po
>           |           |    |------djangojs.po
>           |           |----de-ch  
>           |           |    |------django.po
>           |           |    |------djangojs.po
>           |           |----fr-fr  
>           |                |------django.po
>           |                |------djangojs.po
>           |-----app2
>           |     |-----locale
>           |           |----en-en  
>           |           |    |------django.po
>           |           |    |------djangojs.po
>           |           |----de-ch  
>           |           |    |------django.po
>           |           |    |------djangojs.po
>           |           |----fr-fr  
>           |                |------django.po
>           |                |------djangojs.po
>           |-----app3
>                 |-----locale
>                       |----en-en  
>                       |    |------django.po
>                       |    |------djangojs.po
>                       |----de-ch  
>                       |    |------django.po
>                       |    |------djangojs.po
>                       |----fr-fr  
>                            |------django.po
>                            |------djangojs.po

To test it simply do:

`python3 po2csv.py ./test translations.csv`

Edit `translations.csv` at your will and merge the translations back with:

`python3 csv2po.py ./app translations.csv`
