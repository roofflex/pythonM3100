<table border=1>
    <tr>
        <th>title</th>
	<th>author</th>
    </tr>
    %for row in rows1:
        <tr style="background-color:lightgreen;">
	    <td>{{row.title}}</td>
	    <td>{{row.author}}</td>
        </tr>
    %end
    %for row in rows2:
        <tr style="background-color:yellow;">
	    <td>{{row.title}}</td>
	    <td>{{row.author}}</td>
        </tr>
    %end
    %for row in rows3:
        <tr style="background-color:pink;">
	    <td>{{row.title}}</td>
	    <td>{{row.author}}</td>
        </tr>
    %end
</table>
