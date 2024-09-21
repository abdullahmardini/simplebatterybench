# What is this?
I just want to know if the different battery tuning stuff, ie `ppd` vs `tlp` vs `tuneD` actually make any difference, and if there's a difference between them.
Note that your particular laptop model will matter a lot, depending on firmware bugs and how that responds to different tuning knobs. It looks like the defaults are fantastic on Thinkpads.

# TODO
* Improve the sleep check. AMD has a script that measures how long you were actually in s2idle, I should probably figure out how they do that and take inspiration / shameless plagiarize.
* Improve the wake check. Need to prevent suspend in the actual script, improve the wake and idle parts. I ran this with my browser open.

# What did I get?
```
1hour_nothing.txt
Slept for 3600 seconds (probably)
Battery life spent: 0.4815002534211885%
Power spent: 0.19000000000000128Wh
perf score of     events per second: 12595.02
Battery life spent: 14.419665484034468%
Power spent: 5.68Wh

1hour_ppd_balanced.txt
Slept for 3600 seconds (probably)
Battery life spent: 0.45180722891566916%
Power spent: 0.17999999999999972Wh
perf score of     events per second: 11180.90
Battery life spent: 11.77208835341365%
Power spent: 4.68Wh

1hour_ppd_powersave.txt
Slept for 3600 seconds (probably)
Battery life spent: 0.47690763052209206%
Power spent: 0.0Wh
perf score of     events per second:  5395.16
Battery life spent: 7.053212851405625%
Power spent: 3.009999999999998Wh

1hour_tlp_defaults.txt
Slept for 3600 seconds (probably)
Battery life spent: 0.4811344644213733%
Power spent: 0.0Wh
perf score of     events per second: 11184.05
Battery life spent: 11.927070144340334%
Power spent: 4.899999999999999Wh

1hour_tlp_modded.txt
Slept for 3600 seconds (probably)
Battery life spent: 0.5021340697966394%
Power spent: 0.20000000000000284Wh
perf score of     events per second:  5395.19
Battery life spent: 7.054983680642728%
Power spent: 2.799999999999997Wh

1hour_tuned_balanced.txt
Slept for 3600 seconds (probably)
Battery life spent: 0.502638853983413%
Power spent: 0.0Wh
perf score of     events per second: 12456.68
Battery life spent: 14.827846192510677%
Power spent: 6.090000000000003Wh

1hour_tuned_laptop.txt
Slept for 3600 seconds (probably)
Battery life spent: 0.455465587044543%
Power spent: 0.0Wh
perf score of     events per second: 12627.88
Battery life spent: 15.13157894736841%
Power spent: 6.169999999999998Wh
```