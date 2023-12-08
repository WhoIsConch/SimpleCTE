# Example Uses 

As mentioned in [How to Use SimpleCTE](https://github.com/WhoIsConch/SimpleCTE/wiki/How-To-Use-SimpleCTE), not all SimpleCTE fields are required to be used for their developed purpose. For example, during the development of SimpleCTE, the "Type" field of an Organization was meant to be used to categorize organizations to either "Business" or "Community". However, this field can be used to categorize organizations in any way the user would like, including by industry, location, or anything else.

Another example of this is the "Status" field of an Organization or Contact. This field was meant to be used to categorize the status of an organization or contact, such as "Active" or "Inactive". However, this field can be used to categorize organizations or contacts in any way the user would like, including by how many students are currently affiliated with the organization or contact.

Following, you will find a few examples of how SimpleCTE can be used to manage relationships between the CTE department and local community and business partners.

## Joe's Flower Shop

Our good friend, Joe Bloom, has recently opened a flower shop near the local High School. He has been in contact with the school's CTE department, and they decided that high school students will be able to join Joe's Flower Shop's internship program. In addition to the cooperative education opportunity that Joe has opened to the school, he has also decided to provide it with some flowers any time the school needs some, including for dances, graduations, and other events. In return, the high school will hold a fundraiser selling Joe's flowers to raise money for the school and the flower shop every now and then.

To manage this relationship, the CTE department has decided to use SimpleCTE. They have created an Organization for Joe's Flower Shop `[O1]`, and have added Joe Bloom as a Contact `[C1]`. They have also created three Resources associated with Joe's Flower Shop, one for the internship program `[R1]`, one for the flowers Joe will provide the school `[R2]`, and one for the fundraiser `[R3]`. 

The CTE department has also decided to create a custom field for the Organization `[O1]` called "Flower Types". This field will be used to store the types of flowers that Joe's Flower Shop can provide. 

The Internship Resource `[R1]` has been linked to the Organization `[O1]`, and has room for any number of students. The CTE department will create a new Contact to hold information about the students in the internship program and link them to the Internship Resource `[R1]`.

The Flowers Resource `[R2]` has been linked to the Organization `[O1]`, and has a value of "$500/month." 

The Fundraiser Resource `[R3]` has been linked to the Organization `[O1]`, and has a value of "Goal: $1,000/year. Current status: $500 raised."

The school also created an Organization for the school itself `[O2]`, and has linked the Flowers Resource `[R2]` to it. This way, the school can easily keep track of what Joe's Flower Shop can provide to the school. The school also links all of the students who may be participating in any internship programs to the school's Organization `[O2]`. This way, the school can easily keep track of what students are participating in what internship programs. The school makes the `Status` of the students "Student" and creates a custom field, "Student ID," to hold the student's custom ID number. 

Using SimpleCTE, this school's CTE department has an easy and reliable way to track what Joe's Flower Shop can provide to the school, as well as what the school can provide to Joe's Flower Shop. The partnership between the two is now much easier to manage, and both parties are happy with the results.


## The Local Chamber of Commerce

The local Chamber of Commerce has recently reached out to the CTE department of the local high school. They have offered to provide the school with a variety of resources, including a list of local businesses that are willing to provide internships to students, a list of local businesses that are willing to provide donations to the school, and a list of local businesses that are willing to provide guest speakers to the school.

To manage this relationship, the CTE department has decided to use SimpleCTE. They have created an Organization for the Chamber of Commerce `[O1]`, and have added Delilah Lillith from the Chamber of Commerce as a Contact `[C1]`. They have also created three Resources associated with the Chamber of Commerce, one for the community service program `[R1]`, one for the donations `[R2]`, and one for the guest speakers `[R3]`.

The Community Service Resource `[R1]` has been linked to the Organization `[O1]`, and has room for any number of students. The CTE department will create new Contacts to hold information about the students in the community service program and link them to the Community Service Resource `[R1]` and the school's own Organization `[O2]`.

The Donations Resource `[R2]` has been linked to the Organization `[O1]`, and has a value of "$1,000/year."

The Guest Speakers Resource `[R3]` has been linked to the Organization `[O1]`, and has a value of "5 Current Speakers." Contacts for each speaker are also created and linked to this resource.

Using SimpleCTE, this school's CTE department has an easy and reliable way to track what the Chamber of Commerce can provide to the school. The partnership between the two is now much easier to manage, and both parties are happy with the results.

