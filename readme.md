<!--
SPDX-FileCopyrightText: 2023 hugues de keyzer

SPDX-License-Identifier: AGPL-3.0-or-later
-->

# indeksilo

indeksilo allows to generate a multi-level alphabetical index from text in tabular data format.

## introduction

text in tabular data format is text formatted as a table (usually stored as a spreadsheet file), where each row of the table contains one word of the text.
one column contains the actual word as it appears in the text, while other columns may contain more information about the word, like the page and line number where it appears, a cleaned-up form (with uniform casing and no punctuation), its lemma, its grammatical category,…

from text in that format, indeksilo generates an alphabetical index (like the ones that appear at the end of books).
see the example section below for a concrete example.

## features

*   multi-level index generation
*   alphabetical sorting using the unicode collation algorithm
*   right-to-left text support
*   multiple values in parent columns support for agglutinated forms
*   multiple reference support (for example: page, line)
*   grouping of identical references with count
*   total count of form occurences at each parent level
*   filtering with regular expressions

## usage

indeksilo takes an input filename and an output filename as arguments, as well as some options.
input and output files should be in opendocument (.ods) or office open xml (.xlsx) format.
the minimal usage is:

```
indeksilo --ref-col ref --form-col form input.ods output.ods
```
where `ref` is the title of the column (in `input.ods`) that contains the reference to use in the index (the page number, for example) and `form` is title of the column (in `input.ods`) that contains the form that will appear in the index.

to display a full description of the usage syntax:

```
indeksilo --help
```

## example

let’s take the following example text, and say that it appears on line 1 and 2 of page 42:

> la suno brilas hodiaŭ. hieraŭ estis malvarme, sed hodiaŭ estas varme.<br>
> ni estas bonŝancaj!

it must first be converted to this format as `input.ods`:

| page | line | word       | form      | lemma      |
| ---- | ---- | ---------- | --------- | ---------- |
| 42   | 1    | la         | la        | la         |
| 42   | 1    | suno       | suno      | suno       |
| 42   | 1    | brilas     | brilas    | brili      |
| 42   | 1    | hodiaŭ.    | hodiaŭ    | hodiaŭ     |
| 42   | 1    | hieraŭ     | hieraŭ    | hieraŭ     |
| 42   | 1    | estis      | estis     | esti       |
| 42   | 1    | malvarme,  | malvarme  | varma      |
| 42   | 1    | sed        | sed       | sed        |
| 42   | 1    | hodiaŭ     | hodiaŭ    | hodiaŭ     |
| 42   | 1    | estas      | estas     | esti       |
| 42   | 1    | varme.     | varme     | varma      |
| 42   | 2    | ni         | ni        | ni         |
| 42   | 2    | estas      | estas     | esti       |
| 42   | 2    | bonŝancaj! | bonŝancaj | bona+ŝanco |

now, let’s generate the index by calling:

```
indeksilo --ref-col page --ref-col line --parent-col lemma --form-col form --split-char + input.ods output.ods
```

this will generate the following table as `output.ods`:

|    | lemma_count | lemma  | form_count | form      | refs         |
| -- | ----------- | ------ | ---------- | --------- | ------------ |
| 0  | 1           | bona   | 1          | bonŝancaj | 42, 2        |
| 1  | 1           | brili  | 1          | brilas    | 42, 1        |
| 2  | 3           | esti   | 2          | estas     | 42, 1; 42, 2 |
| 3  |             |        | 1          | estis     | 42, 1        |
| 4  | 1           | hieraŭ | 1          | hieraŭ    | 42, 1        |
| 5  | 2           | hodiaŭ | 2          | hodiaŭ    | 42, 1 (2)    |
| 6  | 1           | la     | 1          | la        | 42, 1        |
| 7  | 1           | ni     | 1          | ni        | 42, 2        |
| 8  | 1           | ŝanco  | 1          | bonŝancaj | 42, 2        |
| 9  | 1           | sed    | 1          | sed       | 42, 1        |
| 10 | 1           | suno   | 1          | suno      | 42, 1        |
| 11 | 2           | varma  | 1          | malvarme  | 42, 1        |
| 12 |             |        | 1          | varme     | 42, 1        |

note that “bonŝancaj” appears twice in the index, once under the form “bona” and once under the form “ŝanco”.
this is because the lemma column contained two values, separated by the defined split character.

note that the word “hodiaŭ” appears twice on the same line.
this is why its reference has “(2)” appended to it.

## filtering

indeksilo allows to filter rows based on column values using regular expressions.

for example, using the same input file as in the previous example, let’s say that only noun lemmas should appear.
in this case, they all end with “o”, so this command can be used:

```
indeksilo --ref-col page --ref-col line --parent-col lemma --form-col form --split-char + --filter "lemma:.*o" input.ods output.ods
```

in this example, the argument is quoted to avoid the `*` character to be interpreted by the shell.
this depends on the shell used.

this will generate the following table:

|   | lemma_count | lemma | form_count | form      | refs  |
| - | ----------- | ----- | ---------- | --------- | ----- |
| 0 | 1           | ŝanco | 1          | bonŝancaj | 42, 2 |
| 1 | 1           | suno  | 1          | suno      | 42, 1 |

note that “bonŝancaj” appears only once in this case, because the lemma “bona” was filtered out.

multiple filter arguments may be used.
the format of the filter expressions is `col:regex`, where `col` is a column name and `regex` is a regular expression matching the value (after splitting).
any column of the input table can be used, even those not used by the index.

by default, filtering is inclusive, which means that at least one expression should match for the row to be included.
this behavior can be reversed with `--filter-exclude`.
in this case, any row matching an expression is excluded; only the rows not matching any of the expressions are included.

for example, still using the same input file, let’s say that forms with less than 4 letters should be excluded.
this command can be used:

```
indeksilo --ref-col page --ref-col line --parent-col lemma --form-col form --split-char + --filter "form:.{1,3}" --filter-exclude input.ods output.ods
```

this will generate the following table:

|   | lemma_count | lemma  | form_count | form      | refs         |
| - | ----------- | ------ | ---------- | --------- | ------------ |
| 0 | 1           | bona   | 1          | bonŝancaj | 42, 2        |
| 1 | 1           | brili  | 1          | brilas    | 42, 1        |
| 2 | 3           | esti   | 2          | estas     | 42, 1; 42, 2 |
| 3 |             |        | 1          | estis     | 42, 1        |
| 4 | 1           | hieraŭ | 1          | hieraŭ    | 42, 1        |
| 5 | 2           | hodiaŭ | 2          | hodiaŭ    | 42, 1 (2)    |
| 6 | 1           | ŝanco  | 1          | bonŝancaj | 42, 2        |
| 7 | 1           | suno   | 1          | suno      | 42, 1        |
| 8 | 2           | varma  | 1          | malvarme  | 42, 1        |
| 9 |             |        | 1          | varme     | 42, 1        |

indeksilo uses python’s regular expressions.
their documentation is [here](https://docs.python.org/3/library/re.html).

## credits

This development was funded by Bastien Kindt for the GREgORI Project.<br>
<https://uclouvain.be/fr/instituts-recherche/incal/ciol/gregori-project.html><br>
<https://www.v2.gregoriproject.com/>
