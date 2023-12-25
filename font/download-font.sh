letters=( A B C D E F G H I J K L M N O P Q R S T U V W X Y Z )
for i in "${letters[@]}"
do
    curl -o "${i}.svg" "https://www.templatemaker.nl/singlelinetext/app.php?proze=${i}&font=SquareItalic&standalone=true"
done
