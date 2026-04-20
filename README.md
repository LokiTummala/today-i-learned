# Today I Learned

We constantly learn new things. This is a repo to share those learnings.
TILs are short Markdown documents (a few sentences + example code) explaining
concepts, bits of syntax, commands, or tips we've recently learned.

Today-I-Learned (TIL) is inspired by Thoughbot, TIL is a repository for everyone to share what we have learn today.

This repo has a tool that help you to manage and write down what you learned in scientific way.

# What I learned

| Summary | Value |
| --- | --- |
| Last synced | 2026-04-20 |
| Total entries | 4 |
| Folders with entries | 2 |
| Unique tags | 6 |

## Recent Entries

| Title | Folder | Date | Tags |
| --- | --- | --- | --- |
| [ThunderingHerd](SystemDesign/ThunderingHerd.md) | SystemDesign | 2026-04-20 | `SystemDesign`, `Cache` |
| [HTTP Codes and Methods](SystemDesign/HTTP-Codes-and-Methods.md) | SystemDesign | 2026-04-20 | `SystemDesign`, `HTTP` |
| [BloomFilter](SystemDesign/BloomFilters.md) | SystemDesign | 2026-04-06 | `SystemDesign`, `BloomFilter` |
| [SQL Joins](Database/SQL/SQLJoins.md) | Database/SQL | 2026-04-06 | `Database`, `SQL` |

## Organized by Folder

### [Database/SQL](Database/SQL/README.md)

| Title | Date | Tags | Summary |
| --- | --- | --- | --- |
| [SQL Joins](Database/SQL/SQLJoins.md) | 2026-04-06 | `Database`, `SQL` | source: SQL Queries |

### [SystemDesign](SystemDesign/README.md)

| Title | Date | Tags | Summary |
| --- | --- | --- | --- |
| [ThunderingHerd](SystemDesign/ThunderingHerd.md) | 2026-04-20 | `SystemDesign`, `Cache` | source : ThunderingHerd |
| [HTTP Codes and Methods](SystemDesign/HTTP-Codes-and-Methods.md) | 2026-04-20 | `SystemDesign`, `HTTP` | source : HTTP Codes and Methods |
| [BloomFilter](SystemDesign/BloomFilters.md) | 2026-04-06 | `SystemDesign`, `BloomFilter` | source: BloomFilters |

## Organized by Tag

### `BloomFilter`

- [BloomFilter](SystemDesign/BloomFilters.md) (SystemDesign, 2026-04-06)

### `Cache`

- [ThunderingHerd](SystemDesign/ThunderingHerd.md) (SystemDesign, 2026-04-20)

### `Database`

- [SQL Joins](Database/SQL/SQLJoins.md) (Database/SQL, 2026-04-06)

### `HTTP`

- [HTTP Codes and Methods](SystemDesign/HTTP-Codes-and-Methods.md) (SystemDesign, 2026-04-20)

### `SQL`

- [SQL Joins](Database/SQL/SQLJoins.md) (Database/SQL, 2026-04-06)

### `SystemDesign`

- [ThunderingHerd](SystemDesign/ThunderingHerd.md) (SystemDesign, 2026-04-20)
- [HTTP Codes and Methods](SystemDesign/HTTP-Codes-and-Methods.md) (SystemDesign, 2026-04-20)
- [BloomFilter](SystemDesign/BloomFilters.md) (SystemDesign, 2026-04-06)


# Instruction

- Step 1: Fork this repo (blank-repo with **only tool** and **readme file**).
- Step 2: Start writting down what you learned in **everyday**.
  + Create a **topic** by:

    ```bash
    ./til <CATEGORY> <SUBJECT> [EDITOR]
    ```

    - Ex:

    ```bash
    ./til bash "Bash Conditional Expression" vim
    ```

    - If you tired of typing the quote mark:

    ```bash
    ./til bash Bash-Conditional-Expression
    ./til bash Bash=Conditional=Expression
    ```

    DO NOT mix the `-` and `=` together!
  + It will create 1 file whose name which is the SUBJECT in lower case:  `bash/160510-bash-conditional-expression.md`.
  + **Write** it! **Save** it!
- Step 3: Refresh the indexes by `./til sync`. This updates the root `README.md` and creates missing folder `README.md` files with an editable notes section.
- Step 4: Commit what you learned today by `./til commit`. After that, if you want to push it to _repository_, just **Enter**

# License

© 2018 khanhicetea.
Distributed under the [Creative Commons Attribution License][license].

[license]: http://creativecommons.org/licenses/by/3.0/
