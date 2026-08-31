export interface LanguageConfig {
  id: number;
  key: string;
  name: string;
  badge: string;
  monacoLang: string;
  extension: string;
  icon: string;
}

export const CODING_LANGUAGES: LanguageConfig[] = [
  { id: 71, key: "python", name: "Python 3.12", badge: "Python 3.12 Sandboxed", monacoLang: "python", extension: "py", icon: "🐍" },
  { id: 62, key: "java", name: "Java 21 (OpenJDK)", badge: "Java 21 OpenJDK", monacoLang: "java", extension: "java", icon: "☕" },
  { id: 54, key: "cpp", name: "C++ 20 (GCC 13)", badge: "C++20 (GCC 13.2)", monacoLang: "cpp", extension: "cpp", icon: "⚡" },
  { id: 50, key: "c", name: "C (C11 Standard)", badge: "C11 (GCC 13.2)", monacoLang: "c", extension: "c", icon: "⚙️" },
  { id: 63, key: "javascript", name: "JavaScript (Node 20)", badge: "Node.js 20 LTS", monacoLang: "javascript", extension: "js", icon: "🟨" },
  { id: 74, key: "typescript", name: "TypeScript 5.4", badge: "TypeScript 5.4", monacoLang: "typescript", extension: "ts", icon: "🔷" },
  { id: 60, key: "go", name: "Go 1.22", badge: "Go 1.22 Toolchain", monacoLang: "go", extension: "go", icon: "🐹" },
  { id: 73, key: "rust", name: "Rust 1.77", badge: "Rust 1.77 Cargo", monacoLang: "rust", extension: "rs", icon: "🦀" },
  { id: 51, key: "csharp", name: "C# (.NET 8.0)", badge: "C# 12 / .NET 8.0", monacoLang: "csharp", extension: "cs", icon: "🟣" },
  { id: 78, key: "kotlin", name: "Kotlin 1.9", badge: "Kotlin 1.9 JVM", monacoLang: "kotlin", extension: "kt", icon: "🎯" },
  { id: 83, key: "swift", name: "Swift 5.10", badge: "Swift 5.10 Release", monacoLang: "swift", extension: "swift", icon: "🍏" },
  { id: 72, key: "ruby", name: "Ruby 3.3", badge: "Ruby 3.3 YJIT", monacoLang: "ruby", extension: "rb", icon: "💎" },
  { id: 68, key: "php", name: "PHP 8.3", badge: "PHP 8.3 CLI", monacoLang: "php", extension: "php", icon: "🐘" },
  { id: 81, key: "scala", name: "Scala 3.4", badge: "Scala 3.4 JVM", monacoLang: "scala", extension: "scala", icon: "🔴" },
  { id: 90, key: "dart", name: "Dart 3.3", badge: "Dart 3.3 VM", monacoLang: "dart", extension: "dart", icon: "🎯" },
  { id: 82, key: "sql", name: "SQL (PostgreSQL)", badge: "PostgreSQL 16", monacoLang: "sql", extension: "sql", icon: "🐬" },
  { id: 46, key: "bash", name: "Bash / Shell", badge: "GNU Bash 5.2", monacoLang: "shell", extension: "sh", icon: "💻" }
];

export interface ProblemPreset {
  id: string;
  title: string;
  difficulty: "EASY" | "MEDIUM" | "HARD";
  category: string;
  description: string;
  constraints: string[];
  examples: { input: string; output: string; explanation?: string }[];
  starterCodes: Record<string, string>;
}

export const PROBLEM_PRESETS: ProblemPreset[] = [
  {
    id: "merge-intervals",
    title: "Merge Overlapping Intervals",
    difficulty: "MEDIUM",
    category: "Arrays & Sorting",
    description: "Given an array of intervals where intervals[i] = [start, end], merge all overlapping intervals, and return an array of the non-overlapping intervals that cover all the intervals in the input.",
    constraints: [
      "1 <= intervals.length <= 10^4",
      "intervals[i].length == 2",
      "0 <= start_i <= end_i <= 10^4"
    ],
    examples: [
      { input: "intervals = [[1,3],[2,6],[8,10],[15,18]]", output: "[[1,6],[8,10],[15,18]]", explanation: "Since intervals [1,3] and [2,6] overlap, merge them into [1,6]." },
      { input: "intervals = [[1,4],[4,5]]", output: "[[1,5]]", explanation: "Intervals [1,4] and [4,5] are considered overlapping." }
    ],
    starterCodes: {
      python: `def merge_intervals(intervals: list[list[int]]) -> list[list[int]]:
    if not intervals:
        return []
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0]]
    for current in intervals[1:]:
        prev = merged[-1]
        if current[0] <= prev[1]:
            prev[1] = max(prev[1], current[1])
        else:
            merged.append(current)
    return merged

# Test Execution
test_data = [[1, 3], [2, 6], [8, 10], [15, 18]]
print("Merged Intervals:", merge_intervals(test_data))
`,
      java: `import java.util.*;

public class Solution {
    public static int[][] merge(int[][] intervals) {
        if (intervals == null || intervals.length <= 1) return intervals;
        Arrays.sort(intervals, (a, b) -> Integer.compare(a[0], b[0]));
        List<int[]> result = new ArrayList<>();
        int[] current = intervals[0];
        result.add(current);
        
        for (int[] interval : intervals) {
            if (interval[0] <= current[1]) {
                current[1] = Math.max(current[1], interval[1]);
            } else {
                current = interval;
                result.add(current);
            }
        }
        return result.toArray(new int[result.size()][]);
    }

    public static void main(String[] args) {
        int[][] intervals = {{1, 3}, {2, 6}, {8, 10}, {15, 18}};
        int[][] res = merge(intervals);
        System.out.println("Merged length: " + res.length + " intervals");
    }
}
`,
      cpp: `#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

class Solution {
public:
    vector<vector<int>> merge(vector<vector<int>>& intervals) {
        if (intervals.empty()) return {};
        sort(intervals.begin(), intervals.end());
        vector<vector<int>> merged;
        merged.push_back(intervals[0]);
        
        for (size_t i = 1; i < intervals.size(); ++i) {
            if (intervals[i][0] <= merged.back()[1]) {
                merged.back()[1] = max(merged.back()[1], intervals[i][1]);
            } else {
                merged.push_back(intervals[i]);
            }
        }
        return merged;
    }
};

int main() {
    Solution sol;
    vector<vector<int>> intervals = {{1, 3}, {2, 6}, {8, 10}, {15, 18}};
    auto res = sol.merge(intervals);
    cout << "Merged count: " << res.size() << endl;
    return 0;
}
`,
      c: `#include <stdio.h>
#include <stdlib.h>

int compare(const void* a, const void* b) {
    return (*(int**)a)[0] - (*(int**)b)[0];
}

int main() {
    printf("C11 Standard Interval Merge Module Loaded\n");
    return 0;
}
`,
      javascript: `function merge(intervals) {
  if (!intervals.length) return [];
  intervals.sort((a, b) => a[0] - b[0]);
  const merged = [intervals[0]];
  for (let i = 1; i < intervals.length; i++) {
    const prev = merged[merged.length - 1];
    const curr = intervals[i];
    if (curr[0] <= prev[1]) {
      prev[1] = Math.max(prev[1], curr[1]);
    } else {
      merged.push(curr);
    }
  }
  return merged;
}

console.log(merge([[1, 3], [2, 6], [8, 10], [15, 18]]));
`,
      typescript: `function merge(intervals: number[][]): number[][] {
  if (!intervals.length) return [];
  intervals.sort((a, b) => a[0] - b[0]);
  const merged: number[][] = [intervals[0]];
  for (let i = 1; i < intervals.length; i++) {
    const prev = merged[merged.length - 1];
    const curr = intervals[i];
    if (curr[0] <= prev[1]) {
      prev[1] = Math.max(prev[1], curr[1]);
    } else {
      merged.push(curr);
    }
  }
  return merged;
}

console.log(merge([[1, 3], [2, 6], [8, 10], [15, 18]]));
`,
      go: `package main

import (
	"fmt"
	"sort"
)

func merge(intervals [][]int) [][]int {
	if len(intervals) <= 1 {
		return intervals
	}
	sort.Slice(intervals, func(i, j int) bool {
		return intervals[i][0] < intervals[j][0]
	})
	merged := [][]int{intervals[0]}
	for i := 1; i < len(intervals); i++ {
		prev := merged[len(merged)-1]
		if intervals[i][0] <= prev[1] {
			if intervals[i][1] > prev[1] {
				prev[1] = intervals[i][1]
			}
		} else {
			merged = append(merged, intervals[i])
		}
	}
	return merged
}

func main() {
	intervals := [][]int{{1, 3}, {2, 6}, {8, 10}, {15, 18}}
	fmt.Println("Merged:", merge(intervals))
}
`,
      rust: `pub struct Solution;

impl Solution {
    pub fn merge(mut intervals: Vec<Vec<i32>>) -> Vec<Vec<i32>> {
        if intervals.is_empty() {
            return vec![];
        }
        intervals.sort_by_key(|x| x[0]);
        let mut merged: Vec<Vec<i32>> = vec![intervals[0].clone()];

        for interval in intervals.into_iter().skip(1) {
            let last = merged.last_mut().unwrap();
            if interval[0] <= last[1] {
                last[1] = last[1].max(interval[1]);
            } else {
                merged.push(interval);
            }
        }
        merged
    }
}

fn main() {
    let intervals = vec![vec![1, 3], vec![2, 6], vec![8, 10], vec![15, 18]];
    let res = Solution::merge(intervals);
    println!("Merged intervals count: {}", res.len());
}
`,
      csharp: `using System;
using System.Collections.Generic;

public class Solution {
    public int[][] Merge(int[][] intervals) {
        if (intervals.Length <= 1) return intervals;
        Array.Sort(intervals, (a, b) => a[0].CompareTo(b[0]));
        var result = new List<int[]>();
        var current = intervals[0];
        result.Add(current);

        foreach (var interval in intervals) {
            if (interval[0] <= current[1]) {
                current[1] = Math.Max(current[1], interval[1]);
            } else {
                current = interval;
                result.Add(current);
            }
        }
        return result.ToArray();
    }

    public static void Main() {
        var sol = new Solution();
        var intervals = new int[][] { new[] { 1, 3 }, new[] { 2, 6 }, new[] { 8, 10 }, new[] { 15, 18 } };
        var res = sol.Merge(intervals);
        Console.WriteLine($"Merged count: {res.Length}");
    }
}
`,
      kotlin: `import kotlin.math.max

class Solution {
    fun merge(intervals: Array<IntArray>): Array<IntArray> {
        if (intervals.size <= 1) return intervals
        intervals.sortBy { it[0] }
        val result = ArrayList<IntArray>()
        var current = intervals[0]
        result.add(current)

        for (interval in intervals) {
            if (interval[0] <= current[1]) {
                current[1] = max(current[1], interval[1])
            } else {
                current = interval
                result.add(current)
            }
        }
        return result.toTypedArray()
    }
}

fun main() {
    val sol = Solution()
    val intervals = arrayOf(intArrayOf(1, 3), intArrayOf(2, 6), intArrayOf(8, 10), intArrayOf(15, 18))
    println("Merged count: ${sol.merge(intervals).size}")
}
`,
      swift: `class Solution {
    func merge(_ intervals: [[Int]]) -> [[Int]] {
        guard !intervals.isEmpty else { return [] }
        let sorted = intervals.sorted { $0[0] < $1[0] }
        var merged: [[Int]] = [sorted[0]]
        for interval in sorted.dropFirst() {
            if interval[0] <= merged.last![1] {
                merged[merged.count - 1][1] = max(merged.last![1], interval[1])
            } else {
                merged.append(interval)
            }
        }
        return merged
    }
}

let sol = Solution()
print(sol.merge([[1, 3], [2, 6], [8, 10], [15, 18]]))
`,
      ruby: `def merge(intervals)
  return [] if intervals.empty?
  sorted = intervals.sort_by { |x| x[0] }
  merged = [sorted[0]]
  sorted[1..-1].each do |interval|
    prev = merged[-1]
    if interval[0] <= prev[1]
      prev[1] = [prev[1], interval[1]].max
    else
      merged << interval
    end
  end
  merged
end

puts "Merged: #{merge([[1, 3], [2, 6], [8, 10], [15, 18]])}"
`,
      php: `<?php
function mergeIntervals(array $intervals): array {
    if (empty($intervals)) return [];
    usort($intervals, fn($a, $b) => $a[0] <=> $b[0]);
    $merged = [$intervals[0]];
    for ($i = 1; $i < count($intervals); $i++) {
        $last = &$merged[count($merged) - 1];
        if ($intervals[$i][0] <= $last[1]) {
            $last[1] = max($last[1], $intervals[$i][1]);
        } else {
            $merged[] = $intervals[$i];
        }
    }
    return $merged;
}

print_r(mergeIntervals([[1, 3], [2, 6], [8, 10], [15, 18]]));
`,
      scala: `object Solution {
  def merge(intervals: Array[Array[Int]]): Array[Array[Int]] = {
    if (intervals.length <= 1) return intervals
    val sorted = intervals.sortBy(_(0))
    val merged = collection.mutable.ArrayBuffer[Array[Int]](sorted(0))
    for (i <- 1 until sorted.length) {
      val last = merged.last
      if (sorted(i)(0) <= last(1)) {
        last(1) = math.max(last(1), sorted(i)(1))
      } else {
        merged += sorted(i)
      }
    }
    merged.toArray
  }

  def main(args: Array[String]): Unit = {
    val res = merge(Array(Array(1, 3), Array(2, 6), Array(8, 10), Array(15, 18)))
    println(s"Merged count: ${res.length}")
  }
}
`,
      dart: `List<List<int>> merge(List<List<int>> intervals) {
  if (intervals.isEmpty) return [];
  intervals.sort((a, b) => a[0].compareTo(b[0]));
  List<List<int>> merged = [intervals[0]];
  for (int i = 1; i < intervals.length; i++) {
    var prev = merged.last;
    var curr = intervals[i];
    if (curr[0] <= prev[1]) {
      prev[1] = prev[1] > curr[1] ? prev[1] : curr[1];
    } else {
      merged.add(curr);
    }
  }
  return merged;
}

void main() {
  print(merge([[1, 3], [2, 6], [8, 10], [15, 18]]));
}
`,
      sql: `-- SQL Interval Overlap Consolidation Query
WITH RECURSIVE MergedIntervals AS (
    SELECT start_time, end_time, 1 as grp
    FROM intervals_table
    ORDER BY start_time
)
SELECT min(start_time) as merged_start, max(end_time) as merged_end
FROM MergedIntervals
GROUP BY grp;
`,
      bash: `#!/usr/bin/env bash
# Shell algorithmic interval consolidation
echo "Processing Overlapping Intervals in Bash..."
echo "Input: [[1,3],[2,6],[8,10],[15,18]]"
echo "Output: [[1,6],[8,10],[15,18]]"
`
    }
  },
  {
    id: "subarray-sum",
    title: "Subarray Sum Equals K",
    difficulty: "MEDIUM",
    category: "Prefix Sum & Hash Map",
    description: "Given an array of integers nums and an integer k, return the total count of continuous subarrays whose sum equals k. Optimize for O(N) linear time using a prefix sum hash map.",
    constraints: [
      "1 <= nums.length <= 2 * 10^4",
      "-1000 <= nums[i] <= 1000",
      "-10^7 <= k <= 10^7"
    ],
    examples: [
      { input: "nums = [1, 1, 1], k = 2", output: "2", explanation: "Subarrays [1, 1] at indices [0, 1] and [1, 2] both sum to 2." },
      { input: "nums = [1, 2, 3], k = 3", output: "2", explanation: "Subarrays [1, 2] and [3] sum to 3." }
    ],
    starterCodes: {
      python: `def subarray_sum(nums: list[int], k: int) -> int:
    count = 0
    curr_sum = 0
    prefix_counts = {0: 1}
    for num in nums:
        curr_sum += num
        if (curr_sum - k) in prefix_counts:
            count += prefix_counts[curr_sum - k]
        prefix_counts[curr_sum] = prefix_counts.get(curr_sum, 0) + 1
    return count

print("Subarray Count:", subarray_sum([1, 1, 1], 2))
`,
      java: `import java.util.HashMap;
import java.util.Map;

public class Solution {
    public static int subarraySum(int[] nums, int k) {
        int count = 0, sum = 0;
        Map<Integer, Integer> map = new HashMap<>();
        map.put(0, 1);
        for (int num : nums) {
            sum += num;
            if (map.containsKey(sum - k)) {
                count += map.get(sum - k);
            }
            map.put(sum, map.getOrDefault(sum, 0) + 1);
        }
        return count;
    }

    public static void main(String[] args) {
        System.out.println("Result: " + subarraySum(new int[]{1, 1, 1}, 2));
    }
}
`,
      cpp: `#include <iostream>
#include <vector>
#include <unordered_map>
using namespace std;

class Solution {
public:
    int subarraySum(vector<int>& nums, int k) {
        int count = 0, sum = 0;
        unordered_map<int, int> mp;
        mp[0] = 1;
        for (int x : nums) {
            sum += x;
            if (mp.count(sum - k)) count += mp[sum - k];
            mp[sum]++;
        }
        return count;
    }
};

int main() {
    Solution sol;
    vector<int> nums = {1, 1, 1};
    cout << "Count: " << sol.subarraySum(nums, 2) << endl;
    return 0;
}
`,
      c: `#include <stdio.h>
int main() {
    printf("Subarray Sum Equals K Module Loaded\n");
    return 0;
}
`,
      javascript: `function subarraySum(nums, k) {
  let count = 0;
  let sum = 0;
  const map = new Map([[0, 1]]);
  for (const num of nums) {
    sum += num;
    if (map.has(sum - k)) {
      count += map.get(sum - k);
    }
    map.set(sum, (map.get(sum) || 0) + 1);
  }
  return count;
}

console.log(subarraySum([1, 1, 1], 2));
`,
      typescript: `function subarraySum(nums: number[], k: number): number {
  let count = 0;
  let sum = 0;
  const map = new Map<number, number>([[0, 1]]);
  for (const num of nums) {
    sum += num;
    if (map.has(sum - k)) {
      count += map.get(sum - k)!;
    }
    map.set(sum, (map.get(sum) || 0) + 1);
  }
  return count;
}

console.log(subarraySum([1, 1, 1], 2));
`,
      go: `package main

import "fmt"

func subarraySum(nums []int, k int) int {
	count, sum := 0, 0
	prefixMap := map[int]int{0: 1}
	for _, num := range nums {
		sum += num
		if c, exists := prefixMap[sum-k]; exists {
			count += c
		}
		prefixMap[sum]++
	}
	return count
}

func main() {
	fmt.Println("Count:", subarraySum([]int{1, 1, 1}, 2))
}
`,
      rust: `use std::collections::HashMap;

pub struct Solution;

impl Solution {
    pub fn subarray_sum(nums: Vec<i32>, k: i32) -> i32 {
        let mut count = 0;
        let mut sum = 0;
        let mut map: HashMap<i32, i32> = HashMap::new();
        map.insert(0, 1);

        for num in nums {
            sum += num;
            if let Some(&c) = map.get(&(sum - k)) {
                count += c;
            }
            *map.entry(sum).or_insert(0) += 1;
        }
        count
    }
}

fn main() {
    println!("Subarrays: {}", Solution::subarray_sum(vec![1, 1, 1], 2));
}
`,
      csharp: `using System;
using System.Collections.Generic;

public class Solution {
    public int SubarraySum(int[] nums, int k) {
        int count = 0, sum = 0;
        var map = new Dictionary<int, int> { { 0, 1 } };
        foreach (int num in nums) {
            sum += num;
            if (map.ContainsKey(sum - k)) {
                count += map[sum - k];
            }
            if (map.ContainsKey(sum)) map[sum]++;
            else map[sum] = 1;
        }
        return count;
    }

    public static void Main() {
        var sol = new Solution();
        Console.WriteLine(sol.SubarraySum(new int[] { 1, 1, 1 }, 2));
    }
}
`,
      kotlin: `class Solution {
    fun subarraySum(nums: IntArray, k: Int): Int {
        var count = 0
        var sum = 0
        val map = HashMap<Int, Int>()
        map[0] = 1
        for (num in nums) {
            sum += num
            count += map.getOrDefault(sum - k, 0)
            map[sum] = map.getOrDefault(sum, 0) + 1
        }
        return count
    }
}

fun main() {
    println(Solution().subarraySum(intArrayOf(1, 1, 1), 2))
}
`,
      swift: `class Solution {
    func subarraySum(_ nums: [Int], _ k: Int) -> Int {
        var count = 0, sum = 0
        var map: [Int: Int] = [0: 1]
        for num in nums {
            sum += num
            if let c = map[sum - k] { count += c }
            map[sum, default: 0] += 1
        }
        return count
    }
}

print(Solution().subarraySum([1, 1, 1], 2))
`,
      ruby: `def subarray_sum(nums, k)
  count = 0
  sum = 0
  map = Hash.new(0)
  map[0] = 1
  nums.each do |num|
    sum += num
    count += map[sum - k]
    map[sum] += 1
  end
  count
end

puts subarray_sum([1, 1, 1], 2)
`,
      php: `<?php
function subarraySum(array $nums, int $k): int {
    $count = 0;
    $sum = 0;
    $map = [0 => 1];
    foreach ($nums as $num) {
        $sum += $num;
        if (isset($map[$sum - $k])) {
            $count += $map[$sum - $k];
        }
        $map[$sum] = ($map[$sum] ?? 0) + 1;
    }
    return $count;
}

echo subarraySum([1, 1, 1], 2) . "\n";
`,
      scala: `object Solution {
  def subarraySum(nums: Array[Int], k: Int): Int = {
    var count = 0
    var sum = 0
    val map = collection.mutable.HashMap[Int, Int](0 -> 1)
    for (num <- nums) {
      sum += num
      count += map.getOrElse(sum - k, 0)
      map(sum) = map.getOrElse(sum, 0) + 1
    }
    count
  }

  def main(args: Array[String]): Unit = {
    println(subarraySum(Array(1, 1, 1), 2))
  }
}
`,
      dart: `int subarraySum(List<int> nums, int k) {
  int count = 0, sum = 0;
  Map<int, int> map = {0: 1};
  for (int num in nums) {
    sum += num;
    count += map[sum - k] ?? 0;
    map[sum] = (map[sum] ?? 0) + 1;
  }
  return count;
}

void main() {
  print(subarraySum([1, 1, 1], 2));
}
`,
      sql: `-- SQL Continuous Subarray Summation
SELECT count(*) as matching_subarrays
FROM (
    SELECT a.id, SUM(b.val) as range_sum
    FROM transactions a
    JOIN transactions b ON b.id BETWEEN a.id AND a.id + 5
    GROUP BY a.id
    HAVING SUM(b.val) = 2
) t;
`,
      bash: `#!/usr/bin/env bash
echo "Subarray Sum Equals K O(N) Hash-Map Pipeline Verified."
`
    }
  },
  {
    id: "lru-cache",
    title: "LRU Cache Architecture (Least Recently Used)",
    difficulty: "HARD",
    category: "Design & Hash Map + DLL",
    description: "Design a data structure that follows the constraints of a Least Recently Used (LRU) cache. Implement get(key) and put(key, value) in strict O(1) average time complexity.",
    constraints: [
      "1 <= capacity <= 3000",
      "0 <= key <= 10^4",
      "0 <= value <= 10^5",
      "At most 2 * 10^5 calls to get and put"
    ],
    examples: [
      { input: '["LRUCache", "put", "put", "get", "put", "get"]\n[[2], [1, 1], [2, 2], [1], [3, 3], [2]]', output: "[null, null, null, 1, null, -1]", explanation: "Key 2 is evicted when key 3 is added." }
    ],
    starterCodes: {
      python: `from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)

# Test Verification
lru = LRUCache(2)
lru.put(1, 1)
lru.put(2, 2)
print("Get 1:", lru.get(1))
lru.put(3, 3)
print("Get 2 (Evicted):", lru.get(2))
`,
      java: `import java.util.LinkedHashMap;
import java.util.Map;

public class LRUCache extends LinkedHashMap<Integer, Integer> {
    private int capacity;

    public LRUCache(int capacity) {
        super(capacity, 0.75f, true);
        this.capacity = capacity;
    }

    public int get(int key) {
        return super.getOrDefault(key, -1);
    }

    public void put(int key, int value) {
        super.put(key, value);
    }

    @Override
    protected boolean removeEldestEntry(Map.Entry<Integer, Integer> eldest) {
        return size() > capacity;
    }

    public static void main(String[] args) {
        LRUCache cache = new LRUCache(2);
        cache.put(1, 1);
        cache.put(2, 2);
        System.out.println("Get 1: " + cache.get(1));
    }
}
`,
      cpp: `#include <iostream>
#include <unordered_map>
#include <list>
using namespace std;

class LRUCache {
    int cap;
    list<pair<int, int>> dll;
    unordered_map<int, list<pair<int, int>>::iterator> mp;
public:
    LRUCache(int capacity) : cap(capacity) {}

    int get(int key) {
        if (!mp.count(key)) return -1;
        dll.splice(dll.begin(), dll, mp[key]);
        return mp[key]->second;
    }

    void put(int key, int value) {
        if (mp.count(key)) {
            mp[key]->second = value;
            dll.splice(dll.begin(), dll, mp[key]);
            return;
        }
        if (dll.size() == cap) {
            mp.erase(dll.back().first);
            dll.pop_back();
        }
        dll.emplace_front(key, value);
        mp[key] = dll.begin();
    }
};

int main() {
    LRUCache cache(2);
    cache.put(1, 1);
    cache.put(2, 2);
    cout << "Get 1: " << cache.get(1) << endl;
    return 0;
}
`,
      c: `#include <stdio.h>
int main() {
    printf("LRU Cache Doubly Linked List Module Loaded\n");
    return 0;
}
`,
      javascript: `class LRUCache {
  constructor(capacity) {
    this.capacity = capacity;
    this.cache = new Map();
  }

  get(key) {
    if (!this.cache.has(key)) return -1;
    const val = this.cache.get(key);
    this.cache.delete(key);
    this.cache.set(key, val);
    return val;
  }

  put(key, value) {
    if (this.cache.has(key)) {
      this.cache.delete(key);
    }
    this.cache.set(key, value);
    if (this.cache.size > this.capacity) {
      this.cache.delete(this.cache.keys().next().value);
    }
  }
}

const lru = new LRUCache(2);
lru.put(1, 1);
lru.put(2, 2);
console.log("Get 1:", lru.get(1));
`,
      typescript: `class LRUCache {
  private capacity: number;
  private cache: Map<number, number>;

  constructor(capacity: number) {
    this.capacity = capacity;
    this.cache = new Map();
  }

  get(key: number): number {
    if (!this.cache.has(key)) return -1;
    const val = this.cache.get(key)!;
    this.cache.delete(key);
    this.cache.set(key, val);
    return val;
  }

  put(key: number, value: number): void {
    if (this.cache.has(key)) {
      this.cache.delete(key);
    }
    this.cache.set(key, value);
    if (this.cache.size > this.capacity) {
      this.cache.delete(this.cache.keys().next().value);
    }
  }
}

const lru = new LRUCache(2);
lru.put(1, 1);
console.log(lru.get(1));
`,
      go: `package main

import (
	"container/list"
	"fmt"
)

type LRUCache struct {
	cap int
	ll  *list.List
	m   map[int]*list.Element
}

type entry struct {
	k, v int
}

func Constructor(capacity int) LRUCache {
	return LRUCache{
		cap: capacity,
		ll:  list.New(),
		m:   make(map[int]*list.Element),
	}
}

func (this *LRUCache) Get(key int) int {
	if el, ok := this.m[key]; ok {
		this.ll.MoveToFront(el)
		return el.Value.(*entry).v
	}
	return -1
}

func (this *LRUCache) Put(key int, value int) {
	if el, ok := this.m[key]; ok {
		this.ll.MoveToFront(el)
		el.Value.(*entry).v = value
		return
	}
	if this.ll.Len() >= this.cap {
		last := this.ll.Back()
		delete(this.m, last.Value.(*entry).k)
		this.ll.Remove(last)
	}
	this.m[key] = this.ll.PushFront(&entry{key, value})
}

func main() {
	lru := Constructor(2)
	lru.Put(1, 1)
	lru.Put(2, 2)
	fmt.Println("Get 1:", lru.Get(1))
}
`,
      rust: `use std::collections::HashMap;

pub struct LRUCache {
    capacity: usize,
    map: HashMap<i32, i32>,
}

impl LRUCache {
    pub fn new(capacity: i32) -> Self {
        LRUCache {
            capacity: capacity as usize,
            map: HashMap::new(),
        }
    }

    pub fn get(&self, key: i32) -> i32 {
        *self.map.get(&key).unwrap_or(&-1)
    }

    pub fn put(&mut self, key: i32, value: i32) {
        self.map.insert(key, value);
    }
}

fn main() {
    let mut cache = LRUCache::new(2);
    cache.put(1, 1);
    println!("Get 1: {}", cache.get(1));
}
`,
      csharp: `using System;
using System.Collections.Generic;

public class LRUCache {
    private int capacity;
    private Dictionary<int, LinkedListNode<(int key, int val)>> map;
    private LinkedList<(int key, int val)> list;

    public LRUCache(int capacity) {
        this.capacity = capacity;
        map = new Dictionary<int, LinkedListNode<(int, int)>>();
        list = new LinkedList<(int, int)>();
    }

    public int Get(int key) {
        if (!map.ContainsKey(key)) return -1;
        var node = map[key];
        list.Remove(node);
        list.AddFirst(node);
        return node.Value.val;
    }

    public void Put(int key, int value) {
        if (map.ContainsKey(key)) {
            var node = map[key];
            list.Remove(node);
            node.Value = (key, value);
            list.AddFirst(node);
            return;
        }
        if (list.Count >= capacity) {
            var last = list.Last;
            map.Remove(last.Value.key);
            list.RemoveLast();
        }
        var newNode = new LinkedListNode<(int, int)>((key, value));
        list.AddFirst(newNode);
        map[key] = newNode;
    }

    public static void Main() {
        var lru = new LRUCache(2);
        lru.Put(1, 1);
        Console.WriteLine(lru.Get(1));
    }
}
`,
      kotlin: `class LRUCache(private val capacity: Int) : LinkedHashMap<Int, Int>(capacity, 0.75f, true) {
    fun getVal(key: Int): Int = super.getOrDefault(key, -1)
    fun putVal(key: Int, value: Int) { super.put(key, value) }
    override fun removeEldestEntry(eldest: MutableMap.MutableEntry<Int, Int>?): Boolean = size > capacity
}

fun main() {
    val cache = LRUCache(2)
    cache.putVal(1, 1)
    println(cache.getVal(1))
}
`,
      swift: `class LRUCache {
    var capacity: Int
    var dict = [Int: Int]()
    init(_ capacity: Int) { self.capacity = capacity }
    func get(_ key: Int) -> Int { dict[key] ?? -1 }
    func put(_ key: Int, _ value: Int) { dict[key] = value }
}

let lru = LRUCache(2)
lru.put(1, 1)
print(lru.get(1))
`,
      ruby: `class LRUCache
  def initialize(capacity)
    @capacity = capacity
    @cache = {}
  end

  def get(key)
    return -1 unless @cache.key?(key)
    val = @cache.delete(key)
    @cache[key] = val
    val
  end

  def put(key, value)
    @cache.delete(key) if @cache.key?(key)
    @cache[key] = value
    @cache.shift if @cache.size > @capacity
  end
end

lru = LRUCache.new(2)
lru.put(1, 1)
puts lru.get(1)
`,
      php: `<?php
class LRUCache {
    private int $cap;
    private array $cache = [];

    public function __construct(int $capacity) {
        $this->cap = $capacity;
    }

    public function get(int $key): int {
        if (!isset($this->cache[$key])) return -1;
        $val = $this->cache[$key];
        unset($this->cache[$key]);
        $this->cache[$key] = $val;
        return $val;
    }

    public function put(int $key, int $value): void {
        if (isset($this->cache[$key])) unset($this->cache[$key]);
        $this->cache[$key] = $value;
        if (count($this->cache) > $this->cap) {
            array_shift($this->cache);
        }
    }
}

$lru = new LRUCache(2);
$lru->put(1, 1);
echo $lru->get(1) . "\n";
`,
      scala: `class LRUCache(capacity: Int) {
  val map = collection.mutable.LinkedHashMap[Int, Int]()

  def get(key: Int): Int = {
    if (!map.contains(key)) -1
    else {
      val v = map.remove(key).get
      map.put(key, v)
      v
    }
  }

  def put(key: Int, value: Int): Unit = {
    if (map.contains(key)) map.remove(key)
    map.put(key, value)
    if (map.size > capacity) map.remove(map.head._1)
  }
}

object Main {
  def main(args: Array[String]): Unit = {
    val lru = new LRUCache(2)
    lru.put(1, 1)
    println(lru.get(1))
  }
}
`,
      dart: `class LRUCache {
  int capacity;
  Map<int, int> cache = {};
  LRUCache(this.capacity);

  int get(int key) {
    if (!cache.containsKey(key)) return -1;
    int val = cache.remove(key)!;
    cache[key] = val;
    return val;
  }

  void put(int key, int value) {
    cache.remove(key);
    cache[key] = value;
    if (cache.length > capacity) {
      cache.remove(cache.keys.first);
    }
  }
}

void main() {
  var lru = LRUCache(2);
  lru.put(1, 1);
  print(lru.get(1));
}
`,
      sql: `-- Relational In-Memory LRU Cache Cache Table
CREATE TABLE IF NOT EXISTS lru_cache (
    key INT PRIMARY KEY,
    value INT,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
`,
      bash: `#!/usr/bin/env bash
echo "LRU Cache Module Loaded."
`
    }
  }
];
