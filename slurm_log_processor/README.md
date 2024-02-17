# How to Use the Log Processor

Inclded in this folder is a file called `process_logs.py` that is inteded to make processing
and collecting statistics on runs a little bit easier. A standard call of the cli is 
as follows:

```
python process_logs.py test_logs/ --stats MaxRSS State --stats-file-name statty_boy.csv
```

Note that the first argument (`test_logs/` in this case), is the directory containing
all of the log files for which you would like to collect the stats.
The `--stats` flag allows for the collection of any of the following stats:

- JobID
- JobName
- Partition
- State
- ExitCode
- Start
- End
- Elapsed
- NCPUS
- NNodes
- NodeList
- ReqMem
- MaxRSS
- AllocCPUS
- Timelimit
- TotalCPU

Note that these are case-sensitive. The result of the call is then saved in a 
CSV-format to the file specified by the flag `--stats-file-name`. In the event
that everything goes well, you will see the something like the following table
in the output *.csv file:

| FileName                                    | JobID  | MaxRSS  | State     |
|---------------------------------------------|--------|---------|-----------|
| 11853384_50x50_grid_to_10_with_200_sims.log | 587102 | 165228K | COMPLETED |
| 4198480_50x50_grid_to_10_with_200_sims.log  | 587097 | 165244K | COMPLETED |
| 60769035_50x50_grid_to_10_with_200_sims.log | 587103 | 165400K | COMPLETED |
| 6714798_50x50_grid_to_10_with_200_sims.log  | 587098 | 165264K | COMPLETED |
| 69447650_50x50_grid_to_10_with_200_sims.log | 587104 | 165268K | COMPLETED |
| 7004921_50x50_grid_to_10_with_200_sims.log  | 587099 | 165256K | COMPLETED |
| 7978400_50x50_grid_to_10_with_200_sims.log  | 587100 | 165268K | COMPLETED |
| 82000180_50x50_grid_to_10_with_200_sims.log | 587105 | 165308K | COMPLETED |
| 8650058_50x50_grid_to_10_with_200_sims.log  | 587101 | 165292K | COMPLETED |
| 96213029_50x50_grid_to_10_with_200_sims.log | 587106 | 165240K | COMPLETED |
| 96471136_50x50_grid_to_10_with_200_sims.log | 587107 | 165284K | COMPLETED |
| bad_log.log                                 | 9587107|         |           |
| no_match.log                                |        |         |           |


