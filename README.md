# pymodiolib

Python modio file format library.


# File Format Overview

Each piece of data is tagged with a 4 character (32 bit) cell so sections of data from different scripts can be named (that's what the _T&lt;M,O,D,1&ht; and _T&lt;M,O,D,2&gt; things were. The weird syntax packs the characters into a single cell.)

The data is stored in a partially non-order-dependent structure since the hook order is usually indeterminate anyway so the tags are used to search for data.

This is what a modio file looks like:
(Actual files are binary, this just represents the structure.)
```
cell            bytes

HEADER
filever         4
numbyte         4
numtags         4
taglist         numtags * 2
[
    tagname     4
    physpos     4
]

BODY
tagbody         numtags * (n tagsize)
[
    tagname     4
    tagsize     4
    tagdata     tagsize
]
```

## Header

- filever (1 cell)
  A single number which identifies which version of modio is required to read the file.

- numbyte (1 cell)
  The size of the header and body in cells (4 bytes per cell).

- numtags (1 cell)
  The number of tags/data sections in the file.

- taglist (numtags * 2 cells)
  A list of tags in the file; each item in this list has two elements:
  tagname (1 cell)
    The 4 character tag name
  physpos (1 cell)
    The physical position of the actual data block (offset from first body cell. First tag always has a physpos of 0)


## Body

- data block
  tagname (1 cell)
    The 4 character tag name
  tagsize (1 cell)
    The amount of cells stored in the block (not including these first two cells)
  tagdata (tagsize cells)
    The actual data


# Function Reference

Main open function:

       Function          |        Description      
------------------------ | ------------------------
open(filename, filemode) | Opens a file, reads the data and returns a ModioSession object instance.


## Class: ModioSession

A ModioSession stores all the information related to a modio file that's open. These objects are created when a file is opened and removed when the file is closed.

    Function Name        |        Description      
------------------------ | ------------------------
close()                  | Closes the session. If the session was opened in write mode, this writes the new data.
get_bytes()              | Returns the raw bytes of the file that will be written.
get(tag)                 | Returns a list containing the data stored in the file under the block named after 'tag' (4 characters). Only works when the file  has been opened in "r"(ead) mode.
put(tag, data)           | Writes 'data' (a list of integers or a single integer) to the file in a block named 'tag' which must be a 4 character string. Only works when the file has been opened in "w"(rite) mode.
metadata()               | Returns the three pieces of data from the file header (file version, size and number of tags).
version()                | Returns the file version,
file_size()              | Returns the size of the file in 32 bit cells (not bytes!)
num_tags()               | Returns the amount of data tags in the open file.


## Class: ModioFileTag

These objects are created to contain single tags and their data. When a file is opened and read, all the data blocks are moved into ModioFileTag objects. These objects can then be interacted with to get their tag name, data and other information.

    Function Name        |        Description      
------------------------ | ------------------------
get_name()               | Return the integer version of the tag name, which is a 32 bit unsigned integer consisting of the 4 character bytes of the name.
get_data()               | Returns the raw data stored in the tag.
get_size()               | Returns the size of the data stored in the tag. This size is representative of the data as a string of 32 bit integers, not bytes!
get_total_size()         | Returns the full size of the tag as it appears in the file (the data size plus the data block header).
get_name_str()           | Returns the name of the tag as a 4 character string.
get_data_block()         | Returns the full data block as it appears in the file as a list of integers.
get_data_format()        | Returns the data in a formatted string suitable for reading.


## Helper functions

    Function Name        |        Description      
------------------------ | ------------------------
_tag_StringToInt(s)      | Converts 's' to an integer. 's' must be a 4 character ASCII string.
_tag_IntToString(i)      | Converts 'i' to a 4 character string 'i' must be a 32 bit integer.
validate_data_block_types(data) | Validates the data stored in a tag block. Decodes strings and ensures the result data is a list of integers.

