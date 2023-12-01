# How to use SimpleCTE

SimpleCTE is built for the Career and Technical Education department of a school. It is designed to be used by teachers and administrators to manage the CTE program's relationships with local community and business partners, as well as managing the resources they provide and the poeple they are associated with. 

## Organizations
Organizations are among the most important aspects of the program. They can be manipulated through the `Organization View` screen after double-clicking an Organization in a table, or by alt-clicking an Organization in a table and selecting the `View` option. Organizations can be created by navigating to the `Organization View` or `Organization Search` screen and selecting the `Add Record` button. 

Organizations have a variety of fields, some of which can be manipulated and used any way the user would like, intended purpose or not. The Name and Type fields are the only required fields of an Organization. The names and purposes of fields available to Organizations are as follows:

| Field | Description | Location |
| --- | --- | --- |
| `Name` | The name of the organization. | Name field, action bar |
| `Type` | The type of organization. | Type field, search screen |
| `Status` | The status of the organization. | Status field, action bar |
| `Primary Phone` | The primary phone number of the organization. Alt-clicking this can reveal a list of all available phone numbers. | Primary Phone field, action bar |
| `Address` | The address of the organization. Alt-clicking this can reveal a list of all available addresses. | Primary Address field, action bar |
| `Organization Contacts` | A table of all available contact information for the organization. Double-clicking or selecting the `View` option of the alt-click menu will bring you to the View screen of the selected Contact. | `Contact Info` table |
| `Associated Resources` | A table of all available resources associated with the organization. Double-clicking or selecting the `View` option of the alt-click menu will bring you to the View screen of the selected Resource. | `Associated Resources` table |
| `Custom Fields` | A table of all available custom fields for the organization. Alt-clicking in the table allows editing, creating, and deleting custom fields | `Custom Fields` table |

## Contacts
Contacts are the people associated with an Organization or Resource. They can be manipulated through the `Contact View` screen after double-clicking a Contact in a table, or by alt-clicking a Contact in a table and selecting the `View` option. Contacts can be created by navigating to the `Contact View` or `Contact Search` screen and selecting the `Add Record` button.

Contacts have a variety of fields, some of which can be manipulated and used any way the user would like, intended purpose or not. The First Name and Last Name fields are the only required fields of a Contact. The names and purposes of fields available to Contacts are as follows:

| Field | Description | Location |
| --- | --- | --- |
| `First Name` | The first name of the contact. | First Name field, action bar |
| `Last Name` | The last name of the contact. | Last Name field, action bar |
| `Status` | The status of the contact. | Status field, action bar |
| `Primary Phone` | The primary phone number of the contact. Alt-clicking this can reveal a list of all available phone numbers. | Primary Phone field, action bar |
| `Address` | The address of the contact. Alt-clicking this can reveal a list of all available addresses. | Primary Address field, action bar |
| `Contact Info` | A table that lists all known contact information for the contact. Alt-clicking in the table allows editing, creating, and deleting contact information. | `Contact Info` table |
| `Organizations` | A table of all organizations associated with the contact. Double-clicking or selecting the `View` option of the alt-click menu will bring you to the View screen of the selected Organization. Linking and unlinking organizations can also be done through the table's alt-click menu. | `Organizations` table | 
| `Associated Resources` | A table of all available resources associated with the contact. Double-clicking or selecting the `View` option of the alt-click menu will bring you to the View screen of the selected Resource. | `Associated Resources` table |
| `Custom Fields` | A table of all available custom fields for the contact. Alt-clicking in the table allows editing, creating, and deleting custom fields | `Custom Fields` table |

## Resources

Resources are the third main object within the program. Resources are used to hold information about what an organization or contact can provide to the CTE department. Resources can be manipulated through the `Resource View` screen after double-clicking a Resource in a table, or by alt-clicking a Resource in a table and selecting the `View` option. Resources can be created by navigating to an Organization or Contact viewer, alt-clicking on the `Associated Resources` table, and selecting "Add Resource."

Resources have the fewest amount of fields, with only a name and value. Both are required, and the value can be as long as you would like. Resources are able to link Organizations and Contacts to it. The names and purposes of fields available to Resources are as follows:

| Field | Description | Location |
| --- | --- | --- |
| `Name` | The name of the resource. | Name field, action bar |
| `Value` | The value of the resource. | Value field, action bar |
| `Organizations` | A table of all organizations associated with the resource. Double-clicking or selecting the `View` option of the alt-click menu will bring you to the View screen of the selected Organization. Linking and unlinking organizations can also be done through the table's alt-click menu. | `Organizations` table |
| `Contacts` | A table of all contacts associated with the resource. Double-clicking or selecting the `View` option of the alt-click menu will bring you to the View screen of the selected Contact. Linking and unlinking contacts can also be done through the table's alt-click menu. | `Contacts` table |

## Example Uses 

As metioned, not all SimpleCTE fields are required to be used for their developed purpose. For example, during the development of SimpleCTE, the "Type" field of an Organization was meant to be used to categorize organizations to either "Business" or "Community". However, this field can be used to categorize organizations in any way the user would like, including by industry, location, or anything else.

Another example of this is the "Status" field of an Organization or Contact. This field was meant to be used to categorize the status of an organization or contact, such as "Active" or "Inactive". However, this field can be used to categorize organizations or contacts in any way the user would like, including by how many students are currently affiliated with the organization or contact.

Following, you will find a few examples of how SimpleCTE can be used to manage relationships between the CTE department and local community and business partners.

### Joe's Flower Shop

Our good friend, Joe Bloom, has recently opened a flower shop near the local High School. He has been in contact with the school's CTE department, and they decided that high school students will be able to join Joe's Flower Shop's internship program. In addition to the cooperative education opportunity that Joe has opened to the school, he has also decided to provide it with some flowers any time the school needs some, including for dances, graduations, and other events. In return, the high school will hold a fundraiser selling Joe's flowers to raise money for the school and the flower shop every now and then.

To manage this relationship, the CTE department has decided to use SimpleCTE. They have created an Organization for Joe's Flower Shop `[O1]`, and have added Joe Bloom as a Contact `[C1]`. They have also created three Resources associated with Joe's Flower Shop, one for the internship program `[R1]`, one for the flowers Joe will provide the school `[R2]`, and one for the fundraiser `[R3]`. 

The CTE department has also decided to create a custom field for the Organization `[O1]` called "Flower Types". This field will be used to store the types of flowers that Joe's Flower Shop can provide. 

The Internship Resource `[R1]` has been linked to the Organization `[O1]`, and has room for any number of students. The CTE department will create a new Contact to hold information about the students in the internship program and link them to the Internship Resource `[R1]`.

The Flowers Resource `[R2]` has been linked to the Organization `[O1]`, and has a value of "$500/month." 

The Fundraiser Resource `[R3]` has been linked to the Organization `[O1]`, and has a value of "Goal: $1,000/year. Current status: $500 raised."

The school also created an Organization for the school itself `[O2]`, and has linked the Flowers Resource `[R2]` to it. This way, the school can easily keep track of what Joe's Flower Shop can provide to the school. The school also links all of the students who may be participating in any internship programs to the school's Organization `[O2]`. This way, the school can easily keep track of what students are participating in what internship programs. The school makes the `Status` of the students "Student" and creates a custom field, "Student ID," to hold the student's custom ID number. 

Using SimpleCTE, this school's CTE department has an easy and reliable way to track what Joe's Flower Shop can provide to the school, as well as what the school can provide to Joe's Flower Shop. The partnership between the two is now much easier to manage, and both parties are happy with the results.


### The Local Chamber of Commerce

The local Chamber of Commerce has recently reached out to the CTE department of the local high school. They have offered to provide the school with a variety of resources, including a list of local businesses that are willing to provide internships to students, a list of local businesses that are willing to provide donations to the school, and a list of local businesses that are willing to provide guest speakers to the school.

To manage this relationship, the CTE department has decided to use SimpleCTE. They have created an Organization for the Chamber of Commerce `[O1]`, and have added the Chamber of Commerce as a Contact `[C1]`. They have also created three Resources associated with the Chamber of Commerce, one for the internship program `[R1]`, one for the donations `[R2]`, and one for the guest speakers `[R3]`.

The Internship Resource `[R1]` has been linked to the Organization `[O1]`, and has room for any number of students. The CTE department will create new Contacts to hold information about the students in the internship program and link them to the Internship Resource `[R1]` and the school's own Organization [O2].

The Donations Resource `[R2]` has been linked to the Organization `[O1]`, and has a value of "$1,000/year."

The Guest Speakers Resource `[R3]` has been linked to the Organization `[O1]`, and has a value of "5 Current Speakers." Contacts for each speaker are also created and linked to this resource.

Using SimpleCTE, this school's CTE department has an easy and reliable way to track what the Chamber of Commerce can provide to the school. The partnership between the two is now much easier to manage, and both parties are happy with the results.

