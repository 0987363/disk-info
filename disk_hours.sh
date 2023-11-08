#!/bin/zsh

for d in /dev/sd?; do
    res="$(smartctl -a $d)"
    model=`echo $res | grep -i 'Device Model' | awk '{print $3,$4}'`
    sn=`echo $res | grep -i 'Serial' | awk '{print $3}'`
    hours=`echo $res | grep -i 'Power_On_Hours' | awk '{print $10}'`
    temp=`echo $res | grep -i 'Temperature_Celsius' | awk '{print $10}'`
    realloc=`echo $res | grep -i 'Reallocated_Sector_Ct' | awk '{print $10}'`
    echo "$d / $model: $temp°C / $hours Hours / Realloc:$realloc"
#    echo "$model($sn): $temp°C $hours Hours"
done


for d in /dev/nvme?; do
    res="$(smartctl -a $d)"
    model=`echo $res | grep -i 'Model Number' | awk '{print $3,$4}'`
    sn=`echo $res | grep -i 'Serial' | awk '{print $3}'`
    hours=`echo $res | grep -i 'Power On Hours' | awk '{print $4}'`
    temp=`echo $res | grep -i 'Temperature:' | awk '{print $2}'`
    realloc=`echo $res | grep -i 'Percentage Used' | awk '{print $3}'`
    echo "$d / $model: $temp°C / $hours Hours / Percentage Used:$realloc"
done

