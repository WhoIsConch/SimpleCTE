# Resources

Resources are one of the main components of SimpleCTE. Resources allow users to manage 
known information about a resource that a partner can provide the school, or vice
versa. For example, a resource could be a cooperative education opportunity with a local
organization, or a scholarship that a student can apply for provided by an organization.

Resources only have a few fields, as they mainly shine in their ability to link Contacts and
Organizations together. Resources can be linked to Contacts and Organizations through the
`Associated Resources` table in the Contact and Organization View screens. Resources can also
be linked to other Resources through the `Associated Resources` table in the Resource View screen.

While in an Organization View or Contact View screen, alt-clicking on a Resource in the table
will reveal five options about managing Resources:

| Option            | Description                                                                       |
|-------------------|-----------------------------------------------------------------------------------|
| `View Resource`   | Brings you to the View screen of the selected Resource.                           |
| `Create Resource` | Creates a new Resource and links it to the current Contact or Organization.       |
| `Link Resource`   | Links a specified Resource to the current Contact or Organization.                |
| `Unlink Resource` | Unlinks the selected Resource from the current Contact or Organization.           |
| `Delete Resource` | Deletes the selected Resource. This removes the resource for every linked object. |

View the [examples](#examples) section for some examples of how to use Resources in a SimpleCTE database.

## Resource Fields

| Field           | Description                                                                                                                                                                                                                                                                              | Location                |
|-----------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------|
| `Name`          | The name of the resource.                                                                                                                                                                                                                                                                | Name field, action bar  |
| `Value`         | The value of the resource.                                                                                                                                                                                                                                                               | Value field, action bar |
| `Organizations` | A table of all organizations associated with the resource. Double-clicking or selecting the `View` option of the alt-click menu will bring you to the View screen of the selected Organization. Linking and unlinking organizations can also be done through the table's alt-click menu. | `Organizations` table   |
| `Contacts`      | A table of all contacts associated with the resource. Double-clicking or selecting the `View` option of the alt-click menu will bring you to the View screen of the selected Contact. Linking and unlinking contacts can also be done through the table's alt-click menu.                | `Contacts` table        |
