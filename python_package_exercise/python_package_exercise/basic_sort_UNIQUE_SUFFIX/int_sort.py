# =========================================================================
#
#  Copyright Ziv Yaniv
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0.txt
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
# =========================================================================

"""
This module sorts lists of integers using bubble sort, quick sort and insertion sort
"""


def bubble(int_list):
    """
    Sorts a list of integers in ascending order using bubble sort.

    Args:
        int_list: List of integers to be stored.

    Returns:
        Sorted list of integers in ascending order

    Raises:
        TypeError: If int_list is not a list or contains non-integer elements.
    """
    n = len(int_list) #length of list
    # Outer loop: Iterate over each element in the list
    for i in range(n): 
            # Inner loop: Traverse the unsorted portion of the list
            # Each pass moves the next largest element to its correct position
            for j in range(0, n-i-1):
                 # If the current element is greater than the next element, swap them
                 if int_list[j] > int_list[j+1]:
                      int_list[j], int_list[j+1] = int_list[j+1], int_list[j] # Swap elements
    return int_list # Return the sorted list


def quick(int_list):
    """
    Sorts a list of integers in ascending order using quick sort.

    Args:
        int_list: List of integers to be sorted

    Returns:
        The sorted list of integers in ascending order.

    Raises:
        TypeError: If int_list is not a list or contains non-integer elements.
    """
    if len(int_list) <= 1: #base case
         return int_list    
    pivot = int_list[len(int_list) // 2] #pivot element(middle of list)
    #partition the list into three sub lists:
    left = [x for x in int_list if x < pivot] #'left' for elements smaller than the pivot
    middle = [x for x in int_list if x == pivot] #'middle' for elements equal to the pivot(handles duplicates)
    right = [x for x in int_list if x > pivot] #'right' for elements greater than the pivot
    #recursively sort 'left' and 'right' sub lists then concatenate
    # results with 'middle to form final sorted list
    return quick(left) + middle + quick(right)


def insertion(int_list):
    """
    Sorts a list of integers in ascending order using insertion sort.

    Args:
        int_lists: List of integers to be sorted.

    Returns:
        The sorted list of integers in ascending order.

    Raises:
        TypeError: If int_list is not a list or contains non-integer elements.
    """
    for i in range(1, len(int_list)):
         # 'key' is the element to be inserted into the sorted portion of the list
         key = int_list[i]
         # 'j' is the index of the last element in the sorted portion of the list
         j = i - 1
         # Move elements of the sorted portion that are greater than 'key'
         #  one position to the right to make space for 'key'
         while j >= 0 and int_list[j] > key:
              int_list[j + 1] = int_list[j] # Shift element at 'j' to the right
              j -= 1 # Move to the next element on the left
         # Place 'key' in its correct position within the sorted portion
         int_list[j +1] = key
    return int_list # Return the sorted list
