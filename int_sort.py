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
This module sorts lists of integers...
"""
from typing import List

def bubble(int_list: List[int]) -> None:
    """
    Will sort a list into smallest to largest integer using bubble sort

    Args:
        int_list: The list that needs to be sorted

    Returns:
        N/A: List is sorted in itself
    """
    n = len(int_list)
    for i in range(n):
        for j in range(0, n - i - 1):
            if int_list[j] > int_list[j + 1]:
                int_list[j], int_list[j + 1] = int_list[j + 1], int_list[j]


def quick(int_list):
    """
    Will sort the input list smallest to largest by using quicksort recursively 

    Args: 
        int_list: The list to be sorted 

    Returns: 
        The function returns a part or the whole list sorted depending on the if statement
    """
    n = len(int_list)
    
    if n <= 1:
        return int_list
    
    else: 
        split = int_list[0]
        left = [x for x in int_list[1:] if x < split]
        right = [x for x in int_list[1:] if x >= split]
        return quick(left) + [split] + quick(right)
    
def insertion(int_list):
    """
        Will sort a list into smallest to largest integer using insertion sort

        Args: 
            int_list: The list that needs to be sorted

        Returns:
            N/A: List is sorted in itself
    """
    for i in range(1, len(int_list)):
        key = int_list[i]
        j = i - 1
        while j >= 0 and key < int_list[j]:
            int_list[j + 1] = int_list[j]
            j -=  1
        int_list[j + 1] = key
